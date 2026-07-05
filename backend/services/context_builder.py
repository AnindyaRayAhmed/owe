import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Synthesizes aggregated civic records into ultra-concise context blocks for Gemini.
    """
    
    @staticmethod
    def build_chat_context(raw_data: dict, chat_history: list = None) -> str:
        """Assembles heavily optimized context for the conversational interface."""
        try:
            acc = raw_data.get("accessibility", [])[:2] # Top 2 only
            trn = raw_data.get("transport", [])[:2]
            env = raw_data.get("environmental", [])[:2]
            mom = raw_data.get("momentum", [])[:2]
            sig = raw_data.get("emerging_signals", [])[:2]
            
            context = "CIVIC CONTEXT:\n"
            
            if sig:
                context += "Alerts:" + ";".join([f"{s.get('type')} in {s.get('neighborhood')}" for s in sig]) + "\n"
                
            if acc:
                context += "Friction:" + ";".join([f"{a.get('neighborhood')}({a.get('issue_type')})" for a in acc]) + "\n"
                
            if trn:
                context += "Traffic:" + ";".join([f"{t.get('neighborhood')}({t.get('avg_density',0):.1f})" for t in trn]) + "\n"
                
            if env:
                context += "Env:" + ";".join([f"{e.get('neighborhood')}(Risk:{e.get('avg_flood_risk',0):.1f})" for e in env]) + "\n"
                
            if mom:
                context += "Momentum:" + ";".join([f"{m.get('detail')} in {m.get('neighborhood')}" for m in mom]) + "\n"
                
        except Exception as e:
            logger.error(f"Error building chat context: {e}")
            context = "Context formatting error."

        history_str = "CHAT HISTORY:\n"
        if chat_history:
            # Only include the last 3 messages to save tokens
            recent_history = chat_history[-3:]
            history_str += "\n".join([f"{msg.get('role')}: {msg.get('content')}" for msg in recent_history])
        else:
            history_str += "(None)\n"
            
        return context + "\n" + history_str
