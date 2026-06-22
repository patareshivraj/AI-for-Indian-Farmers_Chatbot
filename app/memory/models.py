from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.router.intents import Intent
from app.access.models import ToolName

class ConversationState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str
    user_id: int
    active_intent: Optional[Intent] = None
    active_tool: Optional[ToolName] = None
    last_parameters: Dict[str, Any] = Field(default_factory=dict)
    last_response_type: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TrackedEntities(BaseModel):
    model_config = ConfigDict(extra="forbid")
    crop_name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    scheme_category: Optional[str] = None
    pest_name: Optional[str] = None
    disease_name: Optional[str] = None
    fertilizer_name: Optional[str] = None
    soil_type: Optional[str] = None

class UserPreferences(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preferred_language: Optional[str] = "en"
    preferred_district: Optional[str] = None
    preferred_crop: Optional[str] = None
