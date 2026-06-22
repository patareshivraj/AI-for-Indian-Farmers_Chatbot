from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.response.models import ResponsePayload, SupportedLanguage

class LLMRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    response_payload: ResponsePayload
    language: SupportedLanguage
    tone: str = "professional and helpful"
    max_tokens: int = 500

class LLMResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    success: bool
    content: str
    source: str
    model: str
    tokens_used: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    fallback_used: bool = False

class LLMTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model_name: str
    latency_ms: int
    tokens_used: int
    success: bool
    fallback_used: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
