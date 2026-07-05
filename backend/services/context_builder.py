import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Responsible for taking raw civic records (from BigQuery or JSON)
    and synthesizing them into structured context blocks for Gemini.
    """
    
    @staticmethod
    def build_daily_brief_context(raw_data: dict) -> str:
        """Assembles a clean context block for daily brief generation."""
        try:
            acc = [x for x in raw_data.get("accessibility_incidents", []) if x.get("status") != "resolved"]
            trn = [x for x in raw_data.get("transport_congestion", []) if x.get("status") != "resolved"]
            env = [x for x in raw_data.get("environmental_stress", []) if x.get("status") != "resolved"]
            civ = [x for x in raw_data.get("civic_complaints", []) if x.get("status") != "resolved"]
            mom = raw_data.get("momentum", [])
            sen = raw_data.get("community_sentiment", [])
            
            context = "ACTIVE CIVIC INCIDENTS:\n"
            context += f"Accessibility: {len(acc)} active. Details: {[x.get('title') for x in acc]}\n"
            context += f"Transport: {len(trn)} active. Details: {[x.get('title') for x in trn]}\n"
            context += f"Environmental: {len(env)} active. Details: {[x.get('title') for x in env]}\n"
            context += f"Complaints: {len(civ)} active. Details: {[x.get('title') for x in civ]}\n\n"
            
            context += "RECENT MOMENTUM (RESOLVED ISSUES):\n"
            context += f"{[m.get('title') for m in mom]}\n\n"
            
            context += "COMMUNITY SENTIMENT:\n"
            for s in sen:
                context += f"- {s.get('locality')}: {s.get('sentiment')} ({s.get('summary')})\n"
                
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
        acc = [x for x in raw_data.get("accessibility_incidents", []) if x.get("status") != "resolved"]
        civ = [x for x in raw_data.get("civic_complaints", []) if x.get("status") != "resolved"]
        
        context = "AREAS NEEDING SUPPORT:\n"
        context += "Accessibility Barriers:\n"
        for item in acc:
            context += f"- Locality: {item.get('locality')}, Issue: {item.get('title')}, Affected: {item.get('affected_group')}\n"
            
        context += "\nCivic Complaints:\n"
        for item in civ:
            context += f"- Locality: {item.get('locality')}, Issue: {item.get('title')}\n"
            
        return context
