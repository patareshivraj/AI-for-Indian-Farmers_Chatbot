from app.llm.models import LLMRequest, LLMResponse
from app.llm.prompts import Prompts
import json
import time
from datetime import datetime
from groq import Groq
from app.core.config import settings

class ResponseGenerator:
    """Interface to Groq models."""
    
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.model_name = model_name
        self.client = Groq(api_key=settings.groq_api_key)
        
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Calls the Groq LLM."""
        system_prompt = Prompts.SYSTEM_PROMPT.format(tone=request.tone)
        payload_str = json.dumps(request.response_payload.content, ensure_ascii=False, default=str)
        user_prompt = Prompts.USER_PROMPT.format(payload=payload_str, language=request.language.value)
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model=self.model_name,
                temperature=0.0,
                max_tokens=1024,
                timeout=5.0,
            )
            
            output = chat_completion.choices[0].message.content
            tokens_used = chat_completion.usage.total_tokens
            
            return LLMResponse(
                success=request.response_payload.success,
                content=output,
                source=request.response_payload.source,
                model=self.model_name,
                tokens_used=tokens_used,
                generated_at=datetime.utcnow(),
                fallback_used=False
            )
        except Exception as e:
            raise ValueError(f"Groq API Error: {str(e)}")

    def _simulate_llm_response(self, request: LLMRequest) -> str:
        """Stub for actual LLM to allow testing without API keys."""
        payload = request.response_payload
        if not payload.success:
            msg = payload.content.get("message", "Error")
            if "permission" in msg.lower():
                return "You do not have permission to access this information."
            return f"Error: {msg}"
            
        if payload.response_type.value == "CROP_RESPONSE":
            count = payload.content.get("crop_count", 0)
            crops = ", ".join(payload.content.get("crops", []))
            if isinstance(payload.content.get("crops", []), list) and len(payload.content.get("crops", [])) > 0:
                # Format to match acceptance criteria:
                formatted_crops = "\n".join([f"• {c}" for c in payload.content.get("crops")])
                return f"You currently have {count} active crops:\n{formatted_crops}"
            return f"You have {count} active crops: {crops}"
            
        if payload.response_type.value == "MARKET_RESPONSE":
            return "Here is a readable market summary based on your data."
            
        return f"LLM Summary of {payload.title}: {str(payload.content)}"
