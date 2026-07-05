import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Responsible for taking aggregated civic records from BigQuery
    and synthesizing them into structured context blocks for Gemini.
    """
    
    @staticmethod
    def build_daily_brief_context(raw_data: dict) -> str:
        """Assembles a clean context block for daily brief generation."""
        try:
            acc = raw_data.get("accessibility", [])
            trn = raw_data.get("transport", [])
            env = raw_data.get("environmental", [])
            mom = raw_data.get("momentum", [])
            sen = raw_data.get("sentiment", [])
            sig = raw_data.get("emerging_signals", [])
            dash = raw_data.get("dashboard", {})
            
            context = "DASHBOARD METRICS:\n"
            context += f"Active Friction Points: {dash.get('friction_points', 0)}\n"
            context += f"Open Missions: {dash.get('open_missions', 0)}\n"
            context += f"Pulse Score: {dash.get('pulse_score', 0)}\n\n"
            
            context += "EMERGING SIGNALS (HIGH SEVERITY):\n"
            for s in sig:
                context += f"- {s.get('type')} in {s.get('neighborhood')}: {s.get('detail')} at {s.get('timestamp')}\n"
            context += "\n"

            context += "ACTIVE CIVIC INCIDENTS:\n"
            context += f"Accessibility Issues (Top):\n"
            for a in acc:
                context += f"- {a.get('neighborhood')}: {a.get('issue_count')} reports of {a.get('issue_type')} (Severity: {a.get('severity')})\n"
                
            context += f"\nTransport Congestion (Top):\n"
            for t in trn:
                context += f"- {t.get('neighborhood')}: Density {t.get('avg_density', 0):.1f}/10, Bus Delay: {t.get('avg_delay', 0):.0f} min\n"
                
            context += f"\nEnvironmental Stress (Top):\n"
            for e in env:
                context += f"- {e.get('neighborhood')}: Env Score {e.get('avg_env_score', 0):.1f}/10, Flood Risk: {e.get('avg_flood_risk', 0):.1f}/10\n"
            context += "\n"
            
            context += "RECENT MOMENTUM (RESOLVED / COMPLETED):\n"
            for m in mom:
                context += f"- {m.get('type')} in {m.get('neighborhood')}: {m.get('detail')} at {m.get('timestamp')}\n"
            context += "\n"
            
            context += "COMMUNITY SENTIMENT (Past 48h):\n"
            for s in sen:
                context += f"- {s.get('neighborhood')}: Sentiment {s.get('avg_sentiment', 0):.2f}, Frustration {s.get('avg_frustration', 0):.1f}/10\n"
                
            return context
        except Exception as e:
            logger.error(f"Error building daily brief context: {e}")
            return str(raw_data) # Fallback to raw JSON string

    @staticmethod
    def build_chat_context(raw_data: dict, chat_history: list = None) -> str:
        """Assembles context for the conversational interface."""
        base_context = ContextBuilder.build_daily_brief_context(raw_data)
        
        history_str = "CHAT HISTORY:\n"
        if chat_history:
            history_str += "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in chat_history])
        else:
            history_str += "(None)\n"
            
        return base_context + "\n" + history_str

    @staticmethod
    def build_missions_context(raw_data: dict) -> str:
        """Assembles context specific to mission generation."""
        # Focus on unresolved incidents that need community help
        acc = raw_data.get("accessibility", [])
        sig = raw_data.get("emerging_signals", [])
        
        context = "AREAS NEEDING SUPPORT (Based on BigQuery Data):\n"
        context += "Accessibility Barriers:\n"
        for item in acc:
            if item.get('severity') in ['High', 'Critical']:
                context += f"- Locality: {item.get('neighborhood')}, Issue: {item.get('issue_type')} (Count: {item.get('issue_count')})\n"
            
        context += "\nEmerging Severe Signals:\n"
        for item in sig:
            context += f"- Locality: {item.get('neighborhood')}, Type: {item.get('type')}, Detail: {item.get('detail')}\n"
            
        return context
