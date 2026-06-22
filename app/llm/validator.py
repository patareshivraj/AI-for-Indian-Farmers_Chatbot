from app.response.models import ResponsePayload, ResponseType
import json

class PayloadValidator:
    """Validates the structure of the incoming ResponsePayload before LLM execution."""
    
    def validate(self, payload: ResponsePayload) -> bool:
        if not payload:
            return False
        if not payload.response_type or not payload.source or not payload.language:
            return False
        if payload.content is None and payload.response_type != ResponseType.ERROR_RESPONSE:
            return False
        return True

class OutputValidator:
    """Validates the output of the LLM to ensure no extreme hallucinations."""
    
    def validate(self, original_payload: ResponsePayload, generated_text: str) -> bool:
        """
        Basic guard against gross hallucinations. 
        In production, this could involve semantic similarity checks or key-entity extraction 
        to ensure output matches input.
        """
        if not generated_text or len(generated_text.strip()) == 0:
            return False
            
        # Example check: if original payload has numbers, ensure some numbers are in the output
        try:
            payload_str = json.dumps(original_payload.content)
            # Find numbers in payload
            import re
            numbers_in_payload = re.findall(r'\b\d+\b', payload_str)
            # Find numbers in generated text
            numbers_in_text = re.findall(r'\b\d+\b', generated_text)
            
            # Simple heuristic: If there are significant numbers in payload, 
            # some must appear in the text (unless it's an error)
            if numbers_in_payload and original_payload.response_type != ResponseType.ERROR_RESPONSE:
                if not any(num in numbers_in_text for num in set(numbers_in_payload)):
                    return False
        except Exception:
            pass
            
        return True
