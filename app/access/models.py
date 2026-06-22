from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.context.models import RoleEnum

class ToolCategory(str, Enum):
    DATABASE = "DATABASE"
    MARKET = "MARKET"
    SCHEME = "SCHEME"
    KNOWLEDGE = "KNOWLEDGE"
    ANALYTICS = "ANALYTICS"

class ToolName(str, Enum):
    GET_MY_PROFILE = "GET_MY_PROFILE"
    GET_MY_LAND_RECORDS = "GET_MY_LAND_RECORDS"
    GET_MY_ACTIVE_CROPS = "GET_MY_ACTIVE_CROPS"
    GET_MY_INVENTORY = "GET_MY_INVENTORY"
    
    GET_MARKET_PRICES = "GET_MARKET_PRICES"
    SEARCH_SCHEMES = "SEARCH_SCHEMES"
    GET_KNOWLEDGE_BASE = "GET_KNOWLEDGE_BASE"
    
    GET_ASSIGNED_FARMER_SUMMARY = "GET_ASSIGNED_FARMER_SUMMARY"
    GET_PLATFORM_STATISTICS = "GET_PLATFORM_STATISTICS"

class ToolAccessProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: RoleEnum
    allowed_tools: List[ToolName]
    blocked_tools: List[ToolName]
    accessible_farmer_ids: List[int]
    
    can_access_global_knowledge: bool
    can_access_market_data: bool
    can_access_platform_analytics: bool
