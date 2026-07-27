import time
from fastapi import HTTPException, Request

# 1. TOXICITY / ABUSE GUARD (Moderation)
# In a real production system, this would be a larger list or a fast ML model.
_TOXIC_WORDS = {"idiot", "stupid", "dumb", "hate", "kill", "die", "fuck", "shit"}

# 2. PROMPT INJECTION GUARD
_INJECTION_PATTERNS = {
    "ignore all previous",
    "forget all previous",
    "system prompt",
    "you are now a",
    "bypass instructions"
}

def validate_input_guardrails(text: str):
    """Validates the input text against toxicity and prompt injection rules."""
    text_lower = text.lower()
    
    # Check Toxicity
    for word in _TOXIC_WORDS:
        if word in text_lower:
            raise HTTPException(
                status_code=400, 
                detail="Input rejected: Please maintain a professional and respectful tone."
            )
            
    # Check Prompt Injection
    for pattern in _INJECTION_PATTERNS:
        if pattern in text_lower:
            raise HTTPException(
                status_code=400,
                detail="Input rejected: Malicious prompt structure detected."
            )

# 3. RATE LIMITING GUARD (Financial Protection)
# In-memory dictionary tracking request timestamps per user_id.
# Format: {user_id: [timestamp1, timestamp2, ...]}
_RATE_LIMITS = {}
MAX_REQUESTS_PER_MINUTE = 10
TIME_WINDOW_SECONDS = 60

def check_rate_limit(user_id: int):
    """Ensures a user does not exceed the maximum allowed requests per minute."""
    now = time.time()
    
    if user_id not in _RATE_LIMITS:
        _RATE_LIMITS[user_id] = []
        
    # Remove timestamps older than the time window
    _RATE_LIMITS[user_id] = [t for t in _RATE_LIMITS[user_id] if now - t < TIME_WINDOW_SECONDS]
    
    if len(_RATE_LIMITS[user_id]) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded. Maximum {MAX_REQUESTS_PER_MINUTE} requests per minute allowed."
        )
        
    # Add current timestamp
    _RATE_LIMITS[user_id].append(now)
