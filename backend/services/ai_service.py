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
        Synthesizes the daily brief using Gemini based on rich BigQuery context.
        Falls back to deterministic generation if the model is unavailable.
        """
        start_time = time.time()
        raw_data = self.bq_service.fetch_civic_data()
        
        try:
            context = ContextBuilder.build_daily_brief_context(raw_data)
            prompt_template = self._load_prompt("daily_brief_prompt.txt")
            prompt = prompt_template.replace("{civic_context}", context)
            
            # Using fail-fast generation (0 retries)
            api_response = self.gemini_client.generate_json_content(prompt, retries=0)
            if api_response:
                elapsed = time.time() - start_time
                logger.info(f"Total Endpoint Time (get_daily_brief - gemini): {elapsed:.3f}s")
                api_response["source"] = "gemini"
                
                # Merge dynamic insights with hard numeric metrics for the UI
                dashboard = raw_data.get("dashboard", {})
                api_response["pulseScore"] = dashboard.get("pulse_score", api_response.get("pulseScore", 50))
                api_response["frictionPoints"] = dashboard.get("friction_points", api_response.get("frictionPoints", 0))
                api_response["openMissions"] = dashboard.get("open_missions", api_response.get("openMissions", 0))
                api_response["activeNeighbors"] = dashboard.get("active_neighbors", "2,450")
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
                logger.warning(f"Gemini daily brief failed due to: {type(e).__name__} - {e}. Activating fallback.")
                fallback = self._simulate_daily_brief(raw_data)
                elapsed = time.time() - start_time
                logger.info(f"Total Endpoint Time (get_daily_brief - fallback): {elapsed:.3f}s")
                return fallback
            else:
                logger.error(f"Daily brief failed (no fallback allowed): {e}")
                raise e

    def get_missions(self) -> list:
        """
        Synthesizes rich, human-centered community missions using Gemini.
        Falls back to deterministic database mapping if the model fails.
        """
        start_time = time.time()
        raw_data = self.bq_service.fetch_civic_data()
        
        try:
            context = ContextBuilder.build_missions_context(raw_data)
            prompt_template = self._load_prompt("mission_generation_prompt.txt")
            prompt = prompt_template.replace("{civic_context}", context)
            
            api_response = self.gemini_client.generate_json_content(prompt, retries=0)
            if api_response:
                elapsed = time.time() - start_time
                logger.info(f"Total Endpoint Time (get_missions - gemini): {elapsed:.3f}s")
                if isinstance(api_response, list):
                    return api_response
                elif "missions" in api_response:
                    return api_response["missions"]
                else:
                    raise GeminiException("Missions JSON lacks expected format.")
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
                logger.warning(f"Gemini missions failed due to: {type(e).__name__} - {e}. Activating fallback.")
                elapsed = time.time() - start_time
                logger.info(f"Total Endpoint Time (get_missions - fallback): {elapsed:.3f}s")
                return raw_data.get("missions", [])
            else:
                logger.error(f"Missions failed (no fallback allowed): {e}")
                raise e

    def chat(self, user_query: str, chat_history: list = None) -> dict:
        """
        GEMINI PATH: Chat continues to use Gemini reasoning based on BigQuery context.
        """
        start_time = time.time()
        raw_data = self.bq_service.fetch_civic_data()
        
        try:
            build_start = time.time()
            context = ContextBuilder.build_chat_context(raw_data, chat_history)
            logger.info(f"Context Build Time: {time.time() - build_start:.3f}s")
            
            prompt_template = self._load_prompt("civic_chat_prompt.txt")
            prompt = (prompt_template
                      .replace("{civic_context}", context)
                      .replace("{user_query}", user_query))
                      
            api_response = self.gemini_client.generate_json_content(prompt, retries=0)
            if api_response and "reply" in api_response:
                elapsed = time.time() - start_time
                logger.info(f"Total Endpoint Time (chat - gemini): {elapsed:.3f}s")
                return {
                    "reply": api_response["reply"],
                    "source": "gemini",
                    "engine": "gemini"
                }
            elif api_response and "response" in api_response:
                elapsed = time.time() - start_time
                logger.info(f"Total Endpoint Time (chat - gemini): {elapsed:.3f}s")
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
                logger.warning(f"Gemini chat failed due to: {type(e).__name__} - {e}. Activating fallback.")
                fallback_response = self._simulate_chat(user_query, raw_data)
                fallback_response["engine"] = "fallback"
                
                elapsed = time.time() - start_time
                logger.info(f"Total Endpoint Time (chat - fallback): {elapsed:.3f}s")
                return fallback_response
            else:
                logger.error(f"Chat failed (no fallback allowed): {e}")
                raise e

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
                "signalStrength": "High" if acc_summary[0].get('severity') == 'Critical' else "Moderate",
                "affectedGroups": "Seniors, Commuters",
                "timeframe": "past 7 days",
                "explainability": f"Aggregated from {acc_summary[0].get('issue_count', 0)} recent incident reports."
            })

        env_stress = raw_data.get("environmental", [])
        if env_stress:
            insights.append({
                "title": f"Environmental stress near {env_stress[0].get('neighborhood', 'the city')}",
                "description": "Elevated scores suggest commuter fatigue and potential weather-related disruption.",
                "signalStrength": "High" if env_stress[0].get('avg_env_score', 0) > 8 else "Moderate",
                "affectedGroups": "Commuters, Local Residents",
                "timeframe": "past 48 hours",
                "explainability": "Derived from real-time environmental score aggregation."
            })

        return {
            "pulseScore": pulse_score,
            "activeNeighbors": "2,450",
            "frictionPoints": total_friction,
            "openMissions": open_missions,
            "insights": insights,
            "momentum": raw_data.get("momentum", []),
            "source": "deterministic"
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
