import pytest
from app.response.models import ResponsePayload, ResponseType, ResponseSource, SupportedLanguage
from app.llm.llm_service import LLMService

@pytest.fixture
def service():
    return LLMService(model_name="gemini-2.5-flash")

# Valid Payload Responses
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
@pytest.mark.parametrize("crop", ["Soybean", "Cotton", "Wheat", "Sugarcane"])
@pytest.mark.parametrize("count", [1, 2, 5, 10])
def test_valid_crop_payload(service, lang, crop, count):
    payload = ResponsePayload(
        success=True,
        response_type=ResponseType.CROP_RESPONSE,
        title="Active Crops",
        content={"crop_count": count, "crops": [crop] * count},
        source=ResponseSource.DATABASE,
        language=lang
    )
    response = service.process(payload)
    assert response.success is True
    assert response.fallback_used is False
    assert response.source == ResponseSource.DATABASE
    assert "active crops" in response.content.lower()

# Empty Payload Validation
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
def test_empty_payload(service, lang):
    payload = ResponsePayload(
        success=True,
        response_type=ResponseType.CROP_RESPONSE,
        title="Active Crops",
        content=None,
        source=ResponseSource.DATABASE,
        language=lang
    )
    response = service.process(payload)
    # Should trigger fallback
    assert response.fallback_used is True

# Fallback Trigger via LLM Error Simulation
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
@pytest.mark.parametrize("intent_type", [ResponseType.MARKET_RESPONSE, ResponseType.SCHEME_RESPONSE])
def test_llm_failure_fallback(service, monkeypatch, lang, intent_type):
    # Force the generator to raise an error
    def mock_generate(*args, **kwargs):
        raise ValueError("Simulated Gemini API Failure")
    
    monkeypatch.setattr(service.generator, "generate", mock_generate)
    
    payload = ResponsePayload(
        success=True,
        response_type=intent_type,
        title="Test Title",
        content={"data": "test"},
        source=ResponseSource.DATABASE,
        language=lang
    )
    response = service.process(payload)
    assert response.fallback_used is True
    assert "Test Title" in response.content

# Error Payload Testing
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
@pytest.mark.parametrize("error_msg", ["Access Denied", "Not Found", "Connection Refused"])
def test_error_payload(service, lang, error_msg):
    payload = ResponsePayload(
        success=False,
        response_type=ResponseType.ERROR_RESPONSE,
        title="Error",
        content={"message": error_msg},
        source=ResponseSource.SYSTEM,
        language=lang
    )
    
    # Even if generator works, the output should reflect the error message safely.
    response = service.process(payload)
    assert response.success is False
    assert "permission" in response.content.lower() or "error" in response.content.lower() or "त्रुटि" in response.content or "त्रुटी" in response.content

# Hallucination Validation
@pytest.mark.parametrize("lang", [SupportedLanguage.EN, SupportedLanguage.HI, SupportedLanguage.MR])
def test_hallucination_validation(service, monkeypatch, lang):
    # Simulate LLM completely dropping the numbers present in payload
    def mock_generate(*args, **kwargs):
        return type("MockResponse", (), {
            "content": "This response has absolutely no digits in it",
            "tokens_used": 10
        })()
        
    monkeypatch.setattr(service.generator, "generate", mock_generate)
    
    payload = ResponsePayload(
        success=True,
        response_type=ResponseType.MARKET_RESPONSE,
        title="Market",
        content={"price": 5000},
        source=ResponseSource.DATABASE,
        language=lang
    )
    response = service.process(payload)
    
    # Depending on how strict the output validator is, 
    # it might trigger fallback because 5000 is missing.
    assert response.fallback_used is True
