from typing import List
from app.router.intents import Intent
from app.router.models import IntentResult
from groq import Groq
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Classifies natural language text into deterministic Intents using 100% Semantic LLM Routing."""

    def __init__(self):
        # We instantiate the client once here to reuse the connection
        self.client = Groq(api_key=settings.groq_api_key)
        
        # We explicitly list all valid intents so the LLM knows the strict boundaries
        self.valid_intents = ", ".join([i.value for i in Intent])
        
        self.system_prompt = (
            "You are Farm360's semantic intent router. Your job is to read the user's agricultural query "
            "and classify it into exactly ONE of the following intents: {}. "
            "CRITICAL RULES: "
            "1. You MUST return ONLY the exact uppercase string of the matched intent. "
            "2. If the user asks about multiple things (e.g., 'crops disease'), pick the most critical or specific intent (DISEASE_QUERY is more specific than CROP_QUERY). "
            "3. If the user is just saying hi, bye, or thanks, pick CHITCHAT_QUERY. "
            "4. If it matches none of these, return UNKNOWN."
        ).format(self.valid_intents)

    def classify(self, text: str) -> IntentResult:
        """Analyzes text semantically via Groq LLM and returns the IntentResult."""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.0,
                max_tokens=20,
                timeout=4.0,
            )
            
            llm_output = chat_completion.choices[0].message.content.strip().upper()
            
            try:
                best_intent = Intent(llm_output)
                confidence = 0.95
                reason = "Classified semantically via primary LLM Router."
            except ValueError:
                best_intent = Intent.UNKNOWN
                confidence = 0.10
                reason = f"LLM returned an invalid intent string: {llm_output}"
                
        except Exception as e:
            logger.error(f"LLM Routing failed: {str(e)}")
            best_intent = Intent.UNKNOWN
            confidence = 0.0
            reason = f"LLM Routing system error: {str(e)}"
            
        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            reason=reason
        )
