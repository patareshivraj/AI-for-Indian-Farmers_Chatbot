from typing import Dict, Type
from app.access.models import ToolName
from app.access.guard import ToolExecutionGuard
from app.tools.base import BaseTool

from app.tools.database.profile_tool import GetMyProfileTool
from app.tools.database.land_tool import GetMyLandRecordsTool
from app.tools.database.crop_tool import GetMyActiveCropsTool
from app.tools.database.inventory_tool import GetMyInventoryTool
from app.tools.database.weather_tool import GetWeatherTool
from app.tools.database.market_tool import GetMarketPricesTool

from app.tools.knowledge.disease_tool import GetDiseaseInfoTool
from app.tools.knowledge.pest_tool import GetPestInfoTool
from app.tools.knowledge.fertilizer_tool import GetFertilizerInfoTool
from app.tools.knowledge.soil_health_tool import GetSoilHealthInfoTool
from app.tools.knowledge.farming_tips_tool import GetFarmingTipsTool

from app.tools.schemes.scheme_search_tool import SchemeSearchTool

class ExecutableToolRegistry:
    """Registry that instantiates executable tools."""
    
    _tool_classes: Dict[ToolName, Type[BaseTool]] = {
        ToolName.GET_MY_PROFILE: GetMyProfileTool,
        ToolName.GET_MY_LAND_RECORDS: GetMyLandRecordsTool,
        ToolName.GET_MY_ACTIVE_CROPS: GetMyActiveCropsTool,
        ToolName.GET_MY_INVENTORY: GetMyInventoryTool,
        ToolName.GET_WEATHER: GetWeatherTool,
        ToolName.GET_MARKET_PRICES: GetMarketPricesTool,
        ToolName.GET_DISEASE_INFO: GetDiseaseInfoTool,
        ToolName.GET_PEST_INFO: GetPestInfoTool,
        ToolName.GET_FERTILIZER_INFO: GetFertilizerInfoTool,
        ToolName.GET_SOIL_HEALTH_INFO: GetSoilHealthInfoTool,
        ToolName.GET_FARMING_TIPS: GetFarmingTipsTool,
        ToolName.SEARCH_SCHEMES: SchemeSearchTool,
    }

    def __init__(self, guard: ToolExecutionGuard, db_session):
        self.guard = guard
        self.db_session = db_session

    def get_tool(self, tool_name: ToolName) -> BaseTool:
        tool_cls = self._tool_classes.get(tool_name)
        if not tool_cls:
            raise ValueError(f"Tool implementation for {tool_name} not found.")
        return tool_cls(guard=self.guard, db_session=self.db_session)
