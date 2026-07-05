import os
import json
import logging
import time
from services.gemini_client import (
    GeminiClient,
    GeminiException,
    GeminiTimeoutError,
    GeminiQuotaError,
    GeminiAuthError,
    GeminiInvalidJSONError
)
from services.bigquery_service import BigQueryService
from services.context_builder import ContextBuilder

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.bq_service = BigQueryService()
        self.prompts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts"
        )

    def _load_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.prompts_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read prompt file {filename}: {e}")
        return ""

    def get_daily_brief(self) -> dict:
        """
        Orchestrates BigQuery -> Context Assembly -> Gemini 2.5 JSON Pipeline
        """
        raw_data = self.bq_service.fetch_civic_data()
        start_time = time.time()
        try:
            context = ContextBuilder.build_daily_brief_context(raw_data)
            prompt_template = self._load_prompt("daily_brief_prompt.txt")
            prompt = prompt_template.replace("{civic_context}", context)
            
            api_response = self.gemini_client.generate_json_content(prompt, retries=1)
            if api_response:
                logger.info("USING GEMINI RESPONSE")
                elapsed = time.time() - start_time
                logger.info(f"Daily brief generation latency: {elapsed:.3f}s")
                api_response["source"] = "gemini"
                return api_response
            else:
                raise GeminiException("Daily brief generated empty response")
        except Exception as e:
            is_fallback_allowed = isinstance(e, (
                GeminiTimeoutError,
                GeminiQuotaError,
                GeminiAuthError,
                GeminiInvalidJSONError
            )) or (not isinstance(e, GeminiException))
            
            if is_fallback_allowed:
                logger.info("USING FALLBACK RESPONSE")
                logger.warning(f"Gemini daily brief failed due to: {type(e).__name__} - {e}. Activating fallback.")
                elapsed = time.time() - start_time
                logger.info(f"Daily brief latency (fallback): {elapsed:.3f}s")
                return self._simulate_daily_brief(raw_data)
            else:
                logger.error(f"Daily brief failed (no fallback allowed): {e}")
                raise e

    def get_missions(self) -> list:
        raw_data = self.bq_service.fetch_civic_data()
        start_time = time.time()
        try:
            context = ContextBuilder.build_missions_context(raw_data)
            prompt_template = self._load_prompt("mission_generation_prompt.txt")
            prompt = prompt_template.replace("{civic_context}", context)
            
            api_response = self.gemini_client.generate_json_content(prompt, retries=1)
            if api_response:
                logger.info("USING GEMINI RESPONSE")
                elapsed = time.time() - start_time
                logger.info(f"Missions generation latency: {elapsed:.3f}s")
                if isinstance(api_response, list):
                    return api_response
                elif "missions" in api_response:
                    return api_response["missions"]
                else:
                    raise GeminiException("Missions JSON lacks expected format (neither list nor key 'missions' present).")
            else:
                raise GeminiException("Missions generated empty response")
        except Exception as e:
            is_fallback_allowed = isinstance(e, (
                GeminiTimeoutError,
                GeminiQuotaError,
                GeminiAuthError,
                GeminiInvalidJSONError
            )) or (not isinstance(e, GeminiException))
            
            if is_fallback_allowed:
                logger.info("USING FALLBACK RESPONSE")
                logger.warning(f"Gemini missions failed due to: {type(e).__name__} - {e}. Activating fallback.")
                elapsed = time.time() - start_time
                logger.info(f"Missions latency (fallback): {elapsed:.3f}s")
                return raw_data.get("missions", [])
            else:
                logger.error(f"Missions failed (no fallback allowed): {e}")
                raise e

    def chat(self, user_query: str, chat_history: list = None) -> dict:
        raw_data = self.bq_service.fetch_civic_data()
        start_time = time.time()
        try:
            context = ContextBuilder.build_chat_context(raw_data, chat_history)
            prompt_template = self._load_prompt("civic_chat_prompt.txt")
            
            prompt = (prompt_template
                      .replace("{civic_context}", context)
                      .replace("{user_query}", user_query))
                      
            # Chat endpoints typically return text, but we enforce JSON wrapper for consistency
            api_response = self.gemini_client.generate_json_content(prompt, retries=1)
            if api_response and "reply" in api_response:
                logger.info("USING GEMINI RESPONSE")
                elapsed = time.time() - start_time
                logger.info(f"Chat response latency: {elapsed:.3f}s")
                return {
                    "reply": api_response["reply"],
                    "source": "gemini",
                    "engine": "gemini"
                }
            elif api_response and "response" in api_response:
                logger.info("USING GEMINI RESPONSE")
                elapsed = time.time() - start_time
                logger.info(f"Chat response latency: {elapsed:.3f}s")
                return {
                    "reply": api_response["response"],
                    "source": "gemini",
                    "engine": "gemini"
                }
            else:
                raise GeminiException("Chat JSON response missing 'reply' or 'response' key.")
        except Exception as e:
            is_fallback_allowed = isinstance(e, (
                GeminiTimeoutError,
                GeminiQuotaError,
                GeminiAuthError,
                GeminiInvalidJSONError
            )) or (not isinstance(e, GeminiException))
            
            if is_fallback_allowed:
                logger.info("USING FALLBACK RESPONSE")
                logger.warning(f"Gemini chat failed due to: {type(e).__name__} - {e}. Activating fallback.")
                elapsed = time.time() - start_time
                logger.info(f"Chat response latency (fallback): {elapsed:.3f}s")
                
                fallback_response = self._simulate_chat(user_query, raw_data)
                fallback_response["engine"] = "fallback"
                return fallback_response
            else:
                logger.error(f"Chat failed (no fallback allowed): {e}")
                raise e

    # --- Deterministic Fallbacks ---
    def _simulate_daily_brief(self, raw_data: dict) -> dict:
        acc_incidents = [x for x in raw_data.get("accessibility_incidents", []) if x.get("status") != "resolved"]
        trans_congestion = [x for x in raw_data.get("transport_congestion", []) if x.get("status") != "resolved"]
        env_stress = [x for x in raw_data.get("environmental_stress", []) if x.get("status") != "resolved"]
        complaints = [x for x in raw_data.get("civic_complaints", []) if x.get("status") != "resolved"]
        
        total_friction = len(acc_incidents) + len(trans_congestion) + len(env_stress) + len(complaints)
        pulse_score = max(50, 100 - (total_friction * 3))

        insights = []
        
        # Kasba Grouping
        kasba_acc = [x for x in acc_incidents if x.get("locality") == "Kasba"]
        if kasba_acc:
            insights.append({
                "title": "Pedestrian barriers emerging in Kasba",
                "description": "Water accumulation seems to be restricting access for seniors, while slow-moving connector traffic adds minor congestion.",
                "signalStrength": "High",
                "affectedGroups": "Seniors, Commuters",
                "timeframe": "today",
                "explainability": f"Recent reports suggest a correlation between {len(kasba_acc)} accessibility barrier and localized transit delays today."
            })
            
        # Jadavpur Grouping
        jadavpur_civ = [x for x in complaints if x.get("locality") == "Jadavpur"]
        if jadavpur_civ:
            insights.append({
                "title": "Streetlight outages causing safety concern in Jadavpur",
                "description": "Late evening access has seen reduced visibility, though local residents appear to be coordinating safety walks.",
                "signalStrength": "Moderate",
                "affectedGroups": "Students",
                "timeframe": "past 48 hours",
                "explainability": "Signals from the past 48 hours point toward unresolved infrastructure gaps, though mitigated by collaborative community action."
            })

        pc_env = [x for x in env_stress if x.get("locality") == "Park Circus"]
        if pc_env:
            insights.append({
                "title": "Commute friction and air stress near Park Circus",
                "description": "Elevated PM2.5 levels are continuing, suggesting moderate commuter fatigue despite easing traffic.",
                "signalStrength": "High",
                "affectedGroups": "Commuters, Local Residents",
                "timeframe": "past 24 hours",
                "explainability": "Aggregated from local air quality indices and historical traffic patterns over the past 24 hours."
            })

        return {
            "pulseScore": pulse_score,
            "activeNeighbors": "1,420",
            "frictionPoints": total_friction,
            "openMissions": len(raw_data.get("missions", [])),
            "insights": insights,
            "momentum": raw_data.get("momentum", []),
            "source": "fallback"
        }
        
    def _simulate_chat(self, user_query: str, raw_data: dict) -> dict:
        query = user_query.lower()
        localities_found = [loc for loc in raw_data.get("localities", []) if loc.lower() in query]
        
        if "improve" in query or "momentum" in query or "resolve" in query:
            reply = (
                "Recent reports suggest strong community momentum and resilience. "
                "For instance, yesterday in Salt Lake, residents planted 50 saplings to improve air quality. "
                "Today, we also noticed that a scattered waste issue in Lake Market was swiftly cleared. "
                "\n\nThese signals from the past 48 hours point toward an active, supportive civic network."
            )
        elif localities_found:
            loc = localities_found[0]
            acc = [x for x in raw_data.get("accessibility_incidents", []) if x.get("locality") == loc]
            momentum = [x for x in raw_data.get("momentum", []) if loc.lower() in x.get("description", "").lower()]
            
            if acc:
                reply = f"Regarding **{loc}**, we've noticed some friction today, primarily around {acc[0]['title']}. These observations are grounded in local civic feeds."
            elif momentum:
                reply = f"Regarding **{loc}**, there is notable positive progress: {momentum[0]['description']}."
            else:
                reply = f"Recent signals from **{loc}** suggest a relatively calm day. We haven't detected significant friction or disruptions."
        else:
            reply = "I am here to help you understand local civic patterns and community momentum in Kolkata."

        return {"reply": reply, "source": "fallback"}
