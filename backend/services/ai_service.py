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
        dashboard = raw_data.get("dashboard", {})
        total_friction = dashboard.get("friction_points", 0)
        pulse_score = dashboard.get("pulse_score", 50)
        open_missions = dashboard.get("open_missions", 0)

        insights = []
        acc_summary = raw_data.get("accessibility", [])
        if acc_summary:
            insights.append({
                "title": f"Accessibility issues in {acc_summary[0].get('neighborhood', 'various areas')}",
                "description": f"Highest reports involve {acc_summary[0].get('issue_type', 'barriers')} affecting local mobility.",
                "signalStrength": "High",
                "affectedGroups": "Seniors, Commuters",
                "timeframe": "past 48 hours",
                "explainability": f"Aggregated from {acc_summary[0].get('issue_count', 0)} recent incident reports."
            })

        env_stress = raw_data.get("environmental", [])
        if env_stress:
            insights.append({
                "title": f"Environmental stress near {env_stress[0].get('neighborhood', 'the city')}",
                "description": "Elevated scores suggest commuter fatigue and potential weather-related disruption.",
                "signalStrength": "Moderate",
                "affectedGroups": "Commuters, Local Residents",
                "timeframe": "past 24 hours",
                "explainability": "Derived from real-time environmental score aggregation."
            })

        return {
            "pulseScore": pulse_score,
            "activeNeighbors": "2,450",
            "frictionPoints": total_friction,
            "openMissions": open_missions,
            "insights": insights,
            "momentum": raw_data.get("momentum", []),
            "source": "fallback"
        }
        
    def _simulate_chat(self, user_query: str, raw_data: dict) -> dict:
        query = user_query.lower()
        if "improve" in query or "momentum" in query or "resolve" in query:
            momentum = raw_data.get("momentum", [])
            details = [m.get("detail", "") for m in momentum[:2]]
            reply = (
                "Recent reports suggest strong community momentum and resilience. "
                f"We noticed these recent wins: {', '.join(details)}. "
                "\n\nThese signals point toward an active, supportive civic network."
            )
        else:
            acc = raw_data.get("accessibility", [])
            if acc:
                reply = f"We've noticed some friction today, primarily around {acc[0].get('issue_type')} in {acc[0].get('neighborhood')}. These observations are grounded in local civic feeds."
            else:
                reply = "I am here to help you understand local civic patterns and community momentum in Kolkata."

        return {"reply": reply, "source": "fallback"}
