import pytest
from app.execution.models import ExecutionResult
from app.router.intents import Intent
from app.access.models import ToolName
from app.response.models import ResponseType, ResponseSource, SupportedLanguage
from app.response.response_engine import ResponseEngine

@pytest.fixture
def engine():
    return ResponseEngine()

# Crop responses (matrix tests)
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
@pytest.mark.parametrize("data", [{"crops": []}, {"crops": ["Soybean", "Cotton"]}])
def test_crop_response(engine, lang, data):
    result = ExecutionResult(
        success=True,
        intent=Intent.CROP_QUERY,
        tool_name=ToolName.GET_MY_ACTIVE_CROPS,
        data=data,
        execution_time_ms=50
    )
    
    payload = engine.generate(result, force_lang=lang)
    
    assert payload.success is True
    assert payload.response_type == ResponseType.CROP_RESPONSE
    assert payload.source == ResponseSource.DATABASE
    assert payload.content == data
    assert payload.language == lang
    if lang == SupportedLanguage.EN:
        assert payload.title == "Active Crops"
    elif lang == SupportedLanguage.HI:
        assert payload.title == "सक्रिय फसलें"
    elif lang == SupportedLanguage.MR:
        assert payload.title == "सक्रिय पिके"

# Market responses (matrix tests)
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
@pytest.mark.parametrize("crop", ["Soybean", "Cotton", "Wheat", "Rice", "Sugarcane"])
def test_market_response(engine, lang, crop):
    result = ExecutionResult(
        success=True,
        intent=Intent.MARKET_QUERY,
        tool_name=ToolName.GET_MARKET_PRICES,
        data={"prices": [f"{crop} price is 5000"]},
        execution_time_ms=20
    )
    
    payload = engine.generate(result, force_lang=lang)
    
    assert payload.success is True
    assert payload.response_type == ResponseType.MARKET_RESPONSE
    assert payload.source == ResponseSource.DATABASE
    assert payload.language == lang

# Scheme responses (matrix tests)
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
@pytest.mark.parametrize("category", ["women", "general", "SC/ST", "irrigation", "equipment"])
def test_scheme_response(engine, lang, category):
    result = ExecutionResult(
        success=True,
        intent=Intent.SCHEME_QUERY,
        tool_name=ToolName.SEARCH_SCHEMES,
        data={"schemes": [f"{category} scheme 1"]},
        execution_time_ms=10
    )
    
    payload = engine.generate(result, force_lang=lang)
    
    assert payload.success is True
    assert payload.response_type == ResponseType.SCHEME_RESPONSE
    assert payload.source == ResponseSource.SCHEME_ENGINE

# Knowledge responses (matrix tests)
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
@pytest.mark.parametrize("tool", [
    ToolName.GET_DISEASE_INFO, 
    ToolName.GET_PEST_INFO, 
    ToolName.GET_FERTILIZER_INFO, 
    ToolName.GET_SOIL_HEALTH_INFO, 
    ToolName.GET_FARMING_TIPS
])
def test_knowledge_responses(engine, lang, tool):
    result = ExecutionResult(
        success=True,
        intent=Intent.GENERAL_AGRICULTURE_QUERY,
        tool_name=tool,
        data={"info": "sample data"},
        execution_time_ms=10
    )
    
    payload = engine.generate(result, force_lang=lang)
    
    assert payload.success is True
    assert payload.response_type == ResponseType.KNOWLEDGE_RESPONSE
    assert payload.source == ResponseSource.KNOWLEDGE_BASE

# Error responses (matrix tests)
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
@pytest.mark.parametrize("error_msg", ["Access denied", "Internal Server Error", "Database failed to connect"])
def test_error_response(engine, lang, error_msg):
    result = ExecutionResult(
        success=False,
        intent=Intent.CROP_QUERY,
        tool_name=ToolName.GET_MY_ACTIVE_CROPS,
        error=error_msg,
        execution_time_ms=10
    )
    
    payload = engine.generate(result, force_lang=lang)
    
    assert payload.success is False
    assert payload.response_type == ResponseType.ERROR_RESPONSE
    
    # Internal stack traces should not leak
    assert payload.content["message"] != error_msg
    
    if "denied" in error_msg.lower():
        assert "permission" in payload.content["message"].lower()

# Unknown Intent / Tool
def test_unknown_response(engine):
    result = ExecutionResult(
        success=True,
        intent=Intent.UNKNOWN,
        tool_name=None,
        data={"foo": "bar"},
        execution_time_ms=10
    )
    
    payload = engine.generate(result, force_lang=SupportedLanguage.EN)
    
    assert payload.success is True
    assert payload.response_type == ResponseType.UNKNOWN_RESPONSE
    assert payload.source == ResponseSource.SYSTEM
