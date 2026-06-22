from typing import Dict
from pydantic import BaseModel, ConfigDict
from app.access.models import ToolName, ToolCategory

class ToolMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: ToolName
    category: ToolCategory
    requires_farmer_context: bool
    requires_assignment_validation: bool

class ToolRegistry:
    """Central registry defining metadata and requirements for every available tool."""
    
    _registry: Dict[ToolName, ToolMetadata] = {
        ToolName.GET_MY_PROFILE: ToolMetadata(
            name=ToolName.GET_MY_PROFILE,
            category=ToolCategory.DATABASE,
            requires_farmer_context=True,
            requires_assignment_validation=False
        ),
        ToolName.GET_MY_LAND_RECORDS: ToolMetadata(
            name=ToolName.GET_MY_LAND_RECORDS,
            category=ToolCategory.DATABASE,
            requires_farmer_context=True,
            requires_assignment_validation=False
        ),
        ToolName.GET_MY_ACTIVE_CROPS: ToolMetadata(
            name=ToolName.GET_MY_ACTIVE_CROPS,
            category=ToolCategory.DATABASE,
            requires_farmer_context=True,
            requires_assignment_validation=False
        ),
        ToolName.GET_MY_INVENTORY: ToolMetadata(
            name=ToolName.GET_MY_INVENTORY,
            category=ToolCategory.DATABASE,
            requires_farmer_context=True,
            requires_assignment_validation=False
        ),
        ToolName.GET_MARKET_PRICES: ToolMetadata(
            name=ToolName.GET_MARKET_PRICES,
            category=ToolCategory.MARKET,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.GET_WEATHER: ToolMetadata(
            name=ToolName.GET_WEATHER,
            category=ToolCategory.DATABASE,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.SEARCH_SCHEMES: ToolMetadata(
            name=ToolName.SEARCH_SCHEMES,
            category=ToolCategory.SCHEME,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.GET_KNOWLEDGE_BASE: ToolMetadata(
            name=ToolName.GET_KNOWLEDGE_BASE,
            category=ToolCategory.KNOWLEDGE,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.GET_DISEASE_INFO: ToolMetadata(
            name=ToolName.GET_DISEASE_INFO,
            category=ToolCategory.KNOWLEDGE,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.GET_PEST_INFO: ToolMetadata(
            name=ToolName.GET_PEST_INFO,
            category=ToolCategory.KNOWLEDGE,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.GET_FERTILIZER_INFO: ToolMetadata(
            name=ToolName.GET_FERTILIZER_INFO,
            category=ToolCategory.KNOWLEDGE,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.GET_SOIL_HEALTH_INFO: ToolMetadata(
            name=ToolName.GET_SOIL_HEALTH_INFO,
            category=ToolCategory.KNOWLEDGE,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.GET_FARMING_TIPS: ToolMetadata(
            name=ToolName.GET_FARMING_TIPS,
            category=ToolCategory.KNOWLEDGE,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
        ToolName.GET_ASSIGNED_FARMER_SUMMARY: ToolMetadata(
            name=ToolName.GET_ASSIGNED_FARMER_SUMMARY,
            category=ToolCategory.DATABASE,
            requires_farmer_context=False,
            requires_assignment_validation=True
        ),
        ToolName.GET_PLATFORM_STATISTICS: ToolMetadata(
            name=ToolName.GET_PLATFORM_STATISTICS,
            category=ToolCategory.ANALYTICS,
            requires_farmer_context=False,
            requires_assignment_validation=False
        ),
    }

    @classmethod
    def get_metadata(cls, tool_name: ToolName) -> ToolMetadata:
        """Fetch metadata for a given tool."""
        return cls._registry[tool_name]

    @classmethod
    def get_all_tools(cls) -> list[ToolName]:
        """Returns a list of all registered tools."""
        return list(cls._registry.keys())
