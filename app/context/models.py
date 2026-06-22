from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class RoleEnum(str, Enum):
    FARMER = "FARMER"
    CONSULTANT = "CONSULTANT"
    ADMIN = "ADMIN"

class LanguageEnum(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"
    # Fallback/Other languages as needed
    OTHER = "other"

class SourceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_type: str = "database"
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class BaseUser(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: int
    role: RoleEnum
    name: str
    mobile_number: Optional[str] = None # Masked
    state: Optional[str] = None
    district: Optional[str] = None
    language: LanguageEnum = LanguageEnum.ENGLISH

class Permissions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    can_access_global_knowledge: bool = True
    can_access_market_prices: bool = True
    can_access_all_aggregates: bool = False

class FarmMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total_land_area_acres: float = 0.0
    active_land_count: int = 0
    active_crops: List[str] = Field(default_factory=list)
    land_ids: List[int] = Field(default_factory=list)

class ConsultantAssignments(BaseModel):
    model_config = ConfigDict(extra="forbid")
    authorized_farmer_ids: List[int] = Field(default_factory=list)

class UserContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    context_version: str = "1.0"
    metadata: SourceMetadata = Field(default_factory=SourceMetadata)
    user: BaseUser
    permissions: Permissions

class FarmerContext(UserContext):
    model_config = ConfigDict(extra="forbid")
    farm_metrics: FarmMetrics

class ConsultantContext(UserContext):
    model_config = ConfigDict(extra="forbid")
    assignments: ConsultantAssignments

class AdminContext(UserContext):
    model_config = ConfigDict(extra="forbid")
    pass
