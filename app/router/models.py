from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, ConfigDict
from app.router.intents import Intent
from app.access.models import ToolName

class IntentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intent: Intent
    confidence: float
    reason: str

class RoutingDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intent: Intent
    tool_name: Optional[ToolName]
    parameters: Dict[str, Any]
    confidence: float

# Typed Parameters
class MarketQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    crop_name: Optional[str] = None
    district: Optional[str] = None

class SchemeQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    state: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None

class DiseaseQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    disease_name: Optional[str] = None
    crop_name: Optional[str] = None

class PestQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pest_name: Optional[str] = None
    crop_name: Optional[str] = None

class WeatherQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    district: Optional[str] = None

class FertilizerQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fertilizer_name: Optional[str] = None
    crop_name: Optional[str] = None

class SoilHealthQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    soil_type: Optional[str] = None

class FarmingTipsQueryParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    crop_name: Optional[str] = None
    month: Optional[str] = None
