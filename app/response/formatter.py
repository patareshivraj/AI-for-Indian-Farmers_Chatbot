from typing import Optional
from app.execution.models import ExecutionResult
from app.response.models import ResponsePayload, ResponseType, SupportedLanguage
from app.access.models import ToolName
from app.response.source_mapper import SourceMapper
from app.response.templates import ResponseTemplates

class ResponseFormatter:
    """Converts ExecutionResults into formatted ResponsePayloads."""
    
    def __init__(self):
        self.source_mapper = SourceMapper()
        self.templates = ResponseTemplates()
        
        self._tool_to_type_mapping = {
            ToolName.GET_MY_PROFILE: ResponseType.PROFILE_RESPONSE,
            ToolName.GET_MY_LAND_RECORDS: ResponseType.LAND_RESPONSE,
            ToolName.GET_MY_ACTIVE_CROPS: ResponseType.CROP_RESPONSE,
            ToolName.GET_MY_INVENTORY: ResponseType.INVENTORY_RESPONSE,
            ToolName.GET_WEATHER: ResponseType.WEATHER_RESPONSE,
            ToolName.GET_MARKET_PRICES: ResponseType.MARKET_RESPONSE,
            ToolName.SEARCH_SCHEMES: ResponseType.SCHEME_RESPONSE,
            ToolName.GET_DISEASE_INFO: ResponseType.KNOWLEDGE_RESPONSE,
            ToolName.GET_PEST_INFO: ResponseType.KNOWLEDGE_RESPONSE,
            ToolName.GET_FERTILIZER_INFO: ResponseType.KNOWLEDGE_RESPONSE,
            ToolName.GET_SOIL_HEALTH_INFO: ResponseType.KNOWLEDGE_RESPONSE,
            ToolName.GET_FARMING_TIPS: ResponseType.KNOWLEDGE_RESPONSE,
        }

    def format_success(self, result: ExecutionResult, lang: SupportedLanguage) -> ResponsePayload:
        response_type = self._tool_to_type_mapping.get(result.tool_name, ResponseType.UNKNOWN_RESPONSE)
        title = self.templates.get_title(response_type, lang)
        source = self.source_mapper.get_source(result.tool_name)
        
        return ResponsePayload(
            success=True,
            response_type=response_type,
            title=title,
            content=result.data,
            source=source,
            language=lang
        )

    def format_error(self, result: ExecutionResult, lang: SupportedLanguage) -> ResponsePayload:
        title = self.templates.get_title(ResponseType.ERROR_RESPONSE, lang)
        source = self.source_mapper.get_source(result.tool_name)
        
        # We sanitize the internal error message to avoid stack traces
        error_content = {"message": "The system encountered an error while retrieving your request."}
        if "denied" in str(result.error).lower() or "unauthorized" in str(result.error).lower():
            error_content["message"] = "Access denied. You do not have permission to view this data."
            
        return ResponsePayload(
            success=False,
            response_type=ResponseType.ERROR_RESPONSE,
            title=title,
            content=error_content,
            source=source,
            language=lang
        )
