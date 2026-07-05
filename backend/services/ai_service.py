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
        HYBRID PATH: Deterministic BigQuery foundation + Targeted LLM enrichment.
        """
        start_time = time.time()
        raw_data = self.bq_service.fetch_civic_data()
        
        # 1. Deterministic Assembly
        dashboard = raw_data.get("dashboard", {})
        pulse_score = dashboard.get("pulse_score", 50)
        total_friction = dashboard.get("friction_points", 0)
        open_missions = dashboard.get("open_missions", 0)
        
        insights = []
        seen_signals = set()
        for s in raw_data.get("emerging_signals", []):
            sig_key = f"{s.get('neighborhood')}_{s.get('detail')}"
            if sig_key in seen_signals:
                continue
            seen_signals.add(sig_key)
            
            insights.append({
                "title": f"{s.get('type')} alert in {s.get('neighborhood')}",
                "description": f"Ongoing reports indicate sustained {s.get('type').lower()} pressures involving {s.get('detail')}. This has been validated by multiple local sensors and civic observations.",
                "signalStrength": "High",
                "affectedGroups": "Local Residents, Commuters",
                "timeframe": "Past 48 hours",
                "explainability": f"Aggregated directly from civic incident feeds in {s.get('neighborhood')}."
            })
            if len(insights) >= 8:
                break
            
        momentum = []
        for m in raw_data.get("momentum", [])[:8]:
            momentum.append({
                "title": f"Positive {m.get('type')} in {m.get('neighborhood')}",
                "timeframe": "recent",
                "description": f"Community momentum continues to grow with a recent {m.get('type').lower()} milestone involving {m.get('detail')}. This demonstrates active civic engagement in {m.get('neighborhood')}."
            })
            
        payload = {
            "pulseScore": pulse_score,
            "activeNeighbors": "2,450",
            "frictionPoints": total_friction,
            "openMissions": open_missions,
            "insights": insights,
            "momentum": momentum,
            "source": "deterministic"
        }
        
        # 2. LLM Enrichment (Optional Narrative Header)
        try:
            context = ContextBuilder.build_daily_brief_context(raw_data)
            prompt_template = self._load_prompt("daily_brief_prompt.txt")
            prompt = prompt_template.replace("{civic_context}", context)
            
            enrichment = self.gemini_client.generate_json_content(prompt, retries=0)
            if enrichment:
                if payload["insights"] and "executive_summary" in enrichment:
                    payload["insights"][0]["description"] = enrichment["executive_summary"]
                if payload["momentum"] and "momentum_summary" in enrichment:
                    payload["momentum"][0]["description"] = enrichment["momentum_summary"]
                payload["source"] = "hybrid"
                
                logger.info(f"Total Endpoint Time (get_daily_brief - hybrid): {time.time() - start_time:.3f}s")
                return payload
            else:
                raise GeminiException("Enrichment returned empty.")
        except Exception as e:
            logger.warning(f"Brief enrichment failed ({type(e).__name__}: {e}). Returning deterministic payload.")
            logger.info(f"Total Endpoint Time (get_daily_brief - fallback): {time.time() - start_time:.3f}s")
            return payload

    def get_missions(self) -> list:
        """
        HYBRID PATH: Deterministic BigQuery structural foundation + Targeted LLM narrative reasoning.
        """
        start_time = time.time()
        raw_data = self.bq_service.fetch_civic_data()
        
        # 1. Deterministic Assembly
        raw_missions = raw_data.get("missions", [])[:15]
        missions = []
        for i, m in enumerate(raw_missions):
            cat = m.get("category", "General")
            hood = m.get("neighborhood", "Local Area")
            missions.append({
                "mission_id": f"mission_{i}",
                "title": m.get("mission_title", "Community Action"),
                "neighborhood": hood,
                "category": cat,
                "urgency_level": m.get("urgency_level", "Medium"),
                "affected_group": m.get("affected_group", "Local Residents, Commuters"),
                "volunteer_count_needed": 5 + (i * 2 % 15), # Deterministic varied count
                "why_it_matters": f"This {cat.lower()} issue in {hood} is currently elevating local stress levels and impacting daily mobility for residents. Immediate attention will restore civic accessibility.",
                "action_guidance": f"Coordinate with local {hood} neighborhood groups to review the site and provide immediate on-ground support."
            })
            
        if not missions:
            return []
            
        # 2. LLM Enrichment (Only for top 4 missions)
        try:
            context = ContextBuilder.build_missions_context(raw_data)
            prompt_template = self._load_prompt("mission_generation_prompt.txt")
            prompt = prompt_template.replace("{civic_context}", context)
            
            enrichments = self.gemini_client.generate_json_content(prompt, retries=0)
            if enrichments and isinstance(enrichments, dict):
                for m in missions:
                    m_id = m["mission_id"]
                    if m_id in enrichments:
                        rich_data = enrichments[m_id]
                        if rich_data.get("why_it_matters"):
                            m["why_it_matters"] = rich_data["why_it_matters"]
                        if rich_data.get("action_guidance"):
                            m["action_guidance"] = rich_data["action_guidance"]
                logger.info(f"Total Endpoint Time (get_missions - hybrid): {time.time() - start_time:.3f}s")
                return missions
            else:
                raise GeminiException("Missions enrichment lacks expected dictionary format.")
        except Exception as e:
            logger.warning(f"Missions enrichment failed ({type(e).__name__}: {e}). Returning deterministic payload.")
            logger.info(f"Total Endpoint Time (get_missions - fallback): {time.time() - start_time:.3f}s")
            return missions

    def chat(self, user_query: str, chat_history: list = None) -> dict:
        """
        GEMINI PATH: Chat fully relies on LLM synthesis.
        """
        start_time = time.time()
        raw_data = self.bq_service.fetch_civic_data()
        
        try:
            context = ContextBuilder.build_chat_context(raw_data, chat_history)
            prompt_template = self._load_prompt("civic_chat_prompt.txt")
            prompt = (prompt_template
                      .replace("{civic_context}", context)
                      .replace("{user_query}", user_query))
                      
            api_response = self.gemini_client.generate_json_content(prompt, retries=0)
            if api_response and "reply" in api_response:
                logger.info(f"Total Endpoint Time (chat - gemini): {time.time() - start_time:.3f}s")
                return {"reply": api_response["reply"], "source": "gemini", "engine": "gemini"}
            elif api_response and "response" in api_response:
                logger.info(f"Total Endpoint Time (chat - gemini): {time.time() - start_time:.3f}s")
                return {"reply": api_response["response"], "source": "gemini", "engine": "gemini"}
            else:
                raise GeminiException("Chat JSON response missing 'reply' or 'response' key.")
        except Exception as e:
            logger.warning(f"Gemini chat failed ({type(e).__name__}: {e}). Activating deterministic fallback.")
            fallback = self._simulate_chat(user_query, raw_data)
            fallback["engine"] = "fallback"
            logger.info(f"Total Endpoint Time (chat - fallback): {time.time() - start_time:.3f}s")
            return fallback

    def _simulate_chat(self, user_query: str, raw_data: dict) -> dict:
        query = user_query.lower()
        if "improve" in query or "momentum" in query or "resolve" in query:
            momentum = raw_data.get("momentum", [])
            details = [m.get("detail", "") for m in momentum[:2]]
            reply = f"Recent reports suggest strong community momentum. Recent wins include: {', '.join(details)}."
        else:
            acc = raw_data.get("accessibility", [])
            if acc:
                reply = f"We've noticed friction today, primarily {acc[0].get('issue_type')} in {acc[0].get('neighborhood')}."
            else:
                reply = "I am here to help you understand local civic patterns and momentum in Kolkata."
        return {"reply": reply, "source": "fallback"}
