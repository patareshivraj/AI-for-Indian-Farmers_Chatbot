from app.access.models import ToolName
from app.response.models import ResponseSource

class SourceMapper:
    """Deterministically maps tool names to their authoritative sources."""
    
    _mapping = {
        ToolName.GET_MY_PROFILE: ResponseSource.DATABASE,
        ToolName.GET_MY_LAND_RECORDS: ResponseSource.DATABASE,
        ToolName.GET_MY_ACTIVE_CROPS: ResponseSource.DATABASE,
        ToolName.GET_MY_INVENTORY: ResponseSource.DATABASE,
        ToolName.GET_WEATHER: ResponseSource.DATABASE,
        ToolName.GET_MARKET_PRICES: ResponseSource.DATABASE,
        ToolName.GET_ASSIGNED_FARMER_SUMMARY: ResponseSource.DATABASE,
        ToolName.GET_PLATFORM_STATISTICS: ResponseSource.DATABASE,
        
        ToolName.GET_DISEASE_INFO: ResponseSource.KNOWLEDGE_BASE,
        ToolName.GET_PEST_INFO: ResponseSource.KNOWLEDGE_BASE,
        ToolName.GET_FERTILIZER_INFO: ResponseSource.KNOWLEDGE_BASE,
        ToolName.GET_SOIL_HEALTH_INFO: ResponseSource.KNOWLEDGE_BASE,
        ToolName.GET_FARMING_TIPS: ResponseSource.KNOWLEDGE_BASE,
        
        ToolName.SEARCH_SCHEMES: ResponseSource.SCHEME_ENGINE,
        ToolName.GET_KNOWLEDGE_BASE: ResponseSource.KNOWLEDGE_BASE,
    }

    def get_source(self, tool_name: ToolName) -> ResponseSource:
        if not tool_name:
            return ResponseSource.SYSTEM
        return self._mapping.get(tool_name, ResponseSource.SYSTEM)
