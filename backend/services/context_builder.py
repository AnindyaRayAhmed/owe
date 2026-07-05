import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Synthesizes aggregated civic records into contextual blocks for Gemini.
    """
    
    @staticmethod
    def build_daily_brief_context(raw_data: dict) -> str:
        """Assembles context specifically for the Dashboard overview."""
        dash = raw_data.get("dashboard", {})
        context = f"DASHBOARD METRICS:\nFriction Points: {dash.get('friction_points', 0)}\nOpen Missions: {dash.get('open_missions', 0)}\nPulse Score: {dash.get('pulse_score', 0)}\n\n"
        
        sig = raw_data.get("emerging_signals", [])[:8]
        if sig:
            context += "EMERGING SIGNALS:\n" + "\n".join([f"- {s.get('type')} in {s.get('neighborhood')}: {s.get('detail')} (Reported: {s.get('timestamp')})" for s in sig]) + "\n\n"
            
        acc = raw_data.get("accessibility", [])[:8]
        if acc:
            context += "RECENT ACCESSIBILITY FRICTION:\n" + "\n".join([f"- {a.get('neighborhood')}: {a.get('severity')} {a.get('issue_type')} (Reports: {a.get('issue_count')})" for a in acc]) + "\n\n"
            
        mom = raw_data.get("momentum", [])[:8]
        if mom:
            context += "COMMUNITY MOMENTUM:\n" + "\n".join([f"- {m.get('detail')} in {m.get('neighborhood')}" for m in mom]) + "\n\n"
            
        return context

    @staticmethod
    def build_missions_context(raw_data: dict) -> str:
        """Assembles rich context specifically for generating community missions."""
        context = "CIVIC SIGNALS FOR MISSIONS:\n\n"
        
        acc = raw_data.get("accessibility", [])[:8]
        if acc:
            context += "ACCESSIBILITY HURDLES:\n" + "\n".join([f"- {a.get('neighborhood')}: {a.get('severity')} {a.get('issue_type')} affecting locals (Reports: {a.get('issue_count')})" for a in acc]) + "\n\n"
            
        env = raw_data.get("environmental", [])[:8]
        if env:
            context += "ENVIRONMENTAL STRESS:\n" + "\n".join([f"- {e.get('neighborhood')}: Avg Flood Risk {e.get('avg_flood_risk',0):.1f}, Avg Env Score {e.get('avg_env_score',0):.1f}" for e in env]) + "\n\n"
            
        trn = raw_data.get("transport", [])[:8]
        if trn:
            context += "TRANSPORTATION FRICTION:\n" + "\n".join([f"- {t.get('neighborhood')}: Avg Delay {t.get('avg_delay',0):.1f}m, Traffic Density {t.get('avg_density',0):.1f}" for t in trn]) + "\n\n"
            
        mom = raw_data.get("momentum", [])[:8]
        if mom:
            context += "RECENT POSITIVE MOMENTUM:\n" + "\n".join([f"- {m.get('detail')} in {m.get('neighborhood')}" for m in mom]) + "\n\n"
            
        return context

    @staticmethod
    def build_chat_context(raw_data: dict, chat_history: list = None) -> str:
        """Assembles heavily optimized context for the conversational interface."""
        try:
            acc = raw_data.get("accessibility", [])[:8]
            trn = raw_data.get("transport", [])[:8]
            env = raw_data.get("environmental", [])[:8]
            mom = raw_data.get("momentum", [])[:8]
            sig = raw_data.get("emerging_signals", [])[:8]
            
            context = "CIVIC CONTEXT:\n"
            
            if sig:
                context += "Alerts:" + "; ".join([f"{s.get('type')} in {s.get('neighborhood')}" for s in sig]) + "\n"
                
            if acc:
                context += "Friction:" + "; ".join([f"{a.get('neighborhood')}({a.get('issue_type')})" for a in acc]) + "\n"
                
            if trn:
                context += "Traffic:" + "; ".join([f"{t.get('neighborhood')}({t.get('avg_density',0):.1f})" for t in trn]) + "\n"
                
            if env:
                context += "Env:" + "; ".join([f"{e.get('neighborhood')}(Risk:{e.get('avg_flood_risk',0):.1f})" for e in env]) + "\n"
                
            if mom:
                context += "Momentum:" + "; ".join([f"{m.get('detail')} in {m.get('neighborhood')}" for m in mom]) + "\n"
                
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
