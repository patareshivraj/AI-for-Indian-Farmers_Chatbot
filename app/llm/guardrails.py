from app.response.models import ResponsePayload
import json

class GroundingGuard:
    """Enforces strict pre-generation grounding rules."""
    
    MAX_PAYLOAD_SIZE_CHARS = 10000

    def check(self, payload: ResponsePayload) -> bool:
        """Returns True if safe to process, False if rejected."""
        
        # 1. Reject empty payloads
        if not payload:
            return False
            
        # 2. Reject if no content and it's supposedly a success
        if payload.success and payload.content is None:
            return False
            
        # 3. Reject oversized payloads
        try:
            payload_str = json.dumps(payload.content, default=str)
            if len(payload_str) > self.MAX_PAYLOAD_SIZE_CHARS:
                return False
        except Exception:
            return False
            
        return True
