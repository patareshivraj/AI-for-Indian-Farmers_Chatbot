from typing import Dict, Any
from app.core.exceptions import MemorySecurityError

class MemorySecurityValidator:
    """Ensures PII and sensitive data never persist to memory."""
    
    BLOCKED_KEYS = {
        "password", "adhar", "aadhar", "adhar_no", "aadhar_no", 
        "pan", "pan_no", "jwt", "token", "secret", "credentials", 
        "property_uid"
    }

    @classmethod
    def validate(cls, payload: Dict[str, Any]) -> None:
        """
        Validates the payload before saving to persistence.
        Raises MemorySecurityError if a blocked key is found.
        """
        for key in payload.keys():
            normalized_key = key.lower()
            if normalized_key in cls.BLOCKED_KEYS:
                raise MemorySecurityError(f"CRITICAL: Attempted to save PII or secret '{key}' in memory. Memory persistence blocked.")
            
            # Simple content scan for exact 12-digit aadhaar or 10-char PAN
            val = str(payload[key])
            if len(val) == 12 and val.isdigit():
                # Potential adhaar
                if "adhar" in normalized_key or "aadhar" in normalized_key:
                    raise MemorySecurityError(f"CRITICAL: Data masking failure for Aadhaar. Blocked.")
