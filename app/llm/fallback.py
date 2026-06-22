from app.response.models import ResponsePayload, SupportedLanguage
import json

class FallbackFormatter:
    """Deterministic formatting if LLM fails."""
    
    def format(self, payload: ResponsePayload) -> str:
        lang = payload.language
        
        if not payload.success:
            msg = payload.content.get("message", "An error occurred.") if payload.content else "An error occurred."
            if lang == SupportedLanguage.HI:
                return f"त्रुटि: {msg}"
            elif lang == SupportedLanguage.MR:
                return f"त्रुटी: {msg}"
            return f"Error: {msg}"
            
        # Very crude deterministic formatting
        if lang == SupportedLanguage.HI:
            result = f"{payload.title}:\n"
        elif lang == SupportedLanguage.MR:
            result = f"{payload.title}:\n"
        else:
            result = f"Here is your {payload.title}:\n"
            
        try:
            if isinstance(payload.content, dict):
                for k, v in payload.content.items():
                    result += f"- {k}: {v}\n"
            elif isinstance(payload.content, list):
                for item in payload.content:
                    result += f"- {item}\n"
            else:
                result += str(payload.content)
        except Exception:
            result += str(payload.content)
            
        return result.strip()
