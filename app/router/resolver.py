from typing import Optional
from app.router.intents import Intent
from app.access.models import ToolName

class ToolResolver:
    """Maps deterministic Intents to executable ToolNames."""
    
    _mapping = {
        Intent.PROFILE_QUERY: ToolName.GET_MY_PROFILE,
        Intent.LAND_QUERY: ToolName.GET_MY_LAND_RECORDS,
        Intent.CROP_QUERY: ToolName.GET_MY_ACTIVE_CROPS,
        Intent.INVENTORY_QUERY: ToolName.GET_MY_INVENTORY,
        
        Intent.WEATHER_QUERY: ToolName.GET_WEATHER,
        Intent.MARKET_QUERY: ToolName.GET_MARKET_PRICES,
        
        Intent.SCHEME_QUERY: ToolName.SEARCH_SCHEMES,
        
        Intent.DISEASE_QUERY: ToolName.GET_DISEASE_INFO,
        Intent.PEST_QUERY: ToolName.GET_PEST_INFO,
        Intent.FERTILIZER_QUERY: ToolName.GET_FERTILIZER_INFO,
        Intent.SOIL_HEALTH_QUERY: ToolName.GET_SOIL_HEALTH_INFO,
        
        Intent.FARMING_TIPS_QUERY: ToolName.GET_FARMING_TIPS,
        
        # Admin / Consultant specific mapped out of generic query if needed,
        # but the intent classification handles it.
    }

    def resolve(self, intent: Intent) -> Optional[ToolName]:
        """Returns the ToolName associated with the intent, if any."""
        return self._mapping.get(intent)
