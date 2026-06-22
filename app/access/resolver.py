from typing import Union
from app.context.models import UserContext, FarmerContext, ConsultantContext, AdminContext, RoleEnum
from app.access.models import ToolAccessProfile, ToolName
from app.access.registry import ToolRegistry

class ToolAccessResolver:
    """Converts a Context object into a deterministic ToolAccessProfile."""

    def resolve(self, context: UserContext) -> ToolAccessProfile:
        role = context.user.role
        all_tools = ToolRegistry.get_all_tools()
        
        allowed_tools = []
        accessible_farmer_ids = []
        
        if isinstance(context, FarmerContext):
            allowed_tools = [
                ToolName.GET_MY_PROFILE,
                ToolName.GET_MY_LAND_RECORDS,
                ToolName.GET_MY_ACTIVE_CROPS,
                ToolName.GET_MY_INVENTORY,
                ToolName.GET_MARKET_PRICES,
                ToolName.GET_WEATHER,
                ToolName.SEARCH_SCHEMES,
                ToolName.GET_KNOWLEDGE_BASE,
                ToolName.GET_DISEASE_INFO,
                ToolName.GET_PEST_INFO,
                ToolName.GET_FERTILIZER_INFO,
                ToolName.GET_SOIL_HEALTH_INFO,
                ToolName.GET_FARMING_TIPS
            ]
            accessible_farmer_ids = [context.user.user_id]
            
        elif isinstance(context, ConsultantContext):
            allowed_tools = [
                ToolName.GET_ASSIGNED_FARMER_SUMMARY,
                ToolName.GET_MARKET_PRICES,
                ToolName.SEARCH_SCHEMES,
                ToolName.GET_KNOWLEDGE_BASE,
                ToolName.GET_DISEASE_INFO,
                ToolName.GET_PEST_INFO,
                ToolName.GET_FERTILIZER_INFO,
                ToolName.GET_SOIL_HEALTH_INFO,
                ToolName.GET_FARMING_TIPS
            ]
            accessible_farmer_ids = context.assignments.authorized_farmer_ids
            
        elif isinstance(context, AdminContext):
            allowed_tools = [
                ToolName.GET_PLATFORM_STATISTICS,
                ToolName.GET_MARKET_PRICES,
                ToolName.SEARCH_SCHEMES,
                ToolName.GET_KNOWLEDGE_BASE,
                ToolName.GET_DISEASE_INFO,
                ToolName.GET_PEST_INFO,
                ToolName.GET_FERTILIZER_INFO,
                ToolName.GET_SOIL_HEALTH_INFO,
                ToolName.GET_FARMING_TIPS
            ]
            
        blocked_tools = [t for t in all_tools if t not in allowed_tools]
        
        return ToolAccessProfile(
            role=role,
            allowed_tools=allowed_tools,
            blocked_tools=blocked_tools,
            accessible_farmer_ids=accessible_farmer_ids,
            can_access_global_knowledge=context.permissions.can_access_global_knowledge,
            can_access_market_data=context.permissions.can_access_market_prices,
            can_access_platform_analytics=context.permissions.can_access_all_aggregates
        )
