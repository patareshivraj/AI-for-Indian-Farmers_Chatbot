from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ResponseType(str, Enum):
    PROFILE_RESPONSE = "PROFILE_RESPONSE"
    LAND_RESPONSE = "LAND_RESPONSE"
    CROP_RESPONSE = "CROP_RESPONSE"
    INVENTORY_RESPONSE = "INVENTORY_RESPONSE"
    WEATHER_RESPONSE = "WEATHER_RESPONSE"
    MARKET_RESPONSE = "MARKET_RESPONSE"
    SCHEME_RESPONSE = "SCHEME_RESPONSE"
    KNOWLEDGE_RESPONSE = "KNOWLEDGE_RESPONSE"
    ERROR_RESPONSE = "ERROR_RESPONSE"
    UNKNOWN_RESPONSE = "UNKNOWN_RESPONSE"

class ResponseSource(str, Enum):
    DATABASE = "DATABASE"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    SCHEME_ENGINE = "SCHEME_ENGINE"
    SYSTEM = "SYSTEM"

class SupportedLanguage(str, Enum):
    EN = "en"
    HI = "hi"
    MR = "mr"

class ResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    success: bool
    response_type: ResponseType
    title: str
    content: Optional[Any] = None
    source: ResponseSource
    language: SupportedLanguage
    generated_at: datetime = Field(default_factory=datetime.utcnow)
