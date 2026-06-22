import pytest
from app.router.router import QueryRouter
from app.router.intents import Intent
from app.access.models import ToolName

@pytest.fixture
def router():
    return QueryRouter()

# Parametrize to easily generate 100+ tests
crop_queries = [
    "What crops do I have?",
    "Show my planted crops",
    "माझी पिके कोणती आहेत?",
    "मेरे खेत में कौनसी फसल है?",
    "List all my crops"
]

market_queries = [
    "Show soybean prices in Pune",
    "What is the market rate for cotton in Nashik?",
    "पुणे मार्केट मध्ये सोयाबीन भाव काय आहे?",
    "सोयाबीन मंडी रेट पुणे",
    "Cotton prices today"
]

scheme_queries = [
    "Women farmer schemes in Maharashtra",
    "Any scheme for women?",
    "मला शासनाच्या योजना सांगा",
    "किसानों के लिए क्या योजना है?",
    "Government subsidies for irrigation"
]

pest_queries = [
    "Tell me about aphids",
    "How to control whitefly in cotton?",
    "माझ्या पिकावर कीड पडली आहे",
    "एफिड्स कीटक",
    "pest control measures"
]

unknown_queries = [
    "Explain quantum entanglement",
    "Who is the president?",
    "How to build a spaceship",
    "Sing me a song",
    "What is the meaning of life?"
]

@pytest.mark.parametrize("query", crop_queries)
def test_crop_queries(router, query):
    decision = router.route(query)
    assert decision.intent == Intent.CROP_QUERY
    assert decision.tool_name == ToolName.GET_MY_ACTIVE_CROPS
    assert decision.confidence >= 0.60

@pytest.mark.parametrize("query", market_queries)
def test_market_queries(router, query):
    decision = router.route(query)
    assert decision.intent == Intent.MARKET_QUERY
    assert decision.tool_name == ToolName.GET_MARKET_PRICES
    assert decision.confidence >= 0.60
    
    # Check extraction for the specific parameterized examples
    if "soybean" in query.lower() or "सोयाबीन" in query:
        assert decision.parameters.get("crop_name") == "soybean"
    if "pune" in query.lower() or "पुणे" in query:
        assert decision.parameters.get("district") == "Pune"

@pytest.mark.parametrize("query", scheme_queries)
def test_scheme_queries(router, query):
    decision = router.route(query)
    assert decision.intent == Intent.SCHEME_QUERY
    assert decision.tool_name == ToolName.SEARCH_SCHEMES
    assert decision.confidence >= 0.60
    
    if "women" in query.lower():
        assert decision.parameters.get("gender") == "female"
    if "maharashtra" in query.lower():
        assert decision.parameters.get("state") == "Maharashtra"

@pytest.mark.parametrize("query", pest_queries)
def test_pest_queries(router, query):
    decision = router.route(query)
    assert decision.intent == Intent.PEST_QUERY
    assert decision.tool_name == ToolName.GET_PEST_INFO
    assert decision.confidence >= 0.60

@pytest.mark.parametrize("query", unknown_queries)
def test_unknown_queries(router, query):
    decision = router.route(query)
    assert decision.intent == Intent.UNKNOWN
    assert decision.tool_name is None
    assert decision.confidence < 0.60

# Add more combinations to reach 100+ test cases easily by matrix multiplication
@pytest.mark.parametrize("crop", ["soybean", "cotton", "wheat", "rice"])
@pytest.mark.parametrize("action", ["show crops", "what crops", "list crops", "my crops", "planted crops"])
def test_matrix_crop_queries(router, crop, action):
    query = f"{action} specifically {crop}"
    decision = router.route(query)
    assert decision.intent == Intent.CROP_QUERY
    assert decision.parameters.get("crop_name") == crop

@pytest.mark.parametrize("district", ["pune", "nashik", "nagpur", "satara"])
@pytest.mark.parametrize("crop", ["soybean", "cotton", "wheat", "rice"])
@pytest.mark.parametrize("phrase", ["price of", "rate of", "market for"])
def test_matrix_market_queries(router, district, crop, phrase):
    query = f"what is the {phrase} {crop} in {district}"
    decision = router.route(query)
    assert decision.intent == Intent.MARKET_QUERY
    assert decision.parameters.get("crop_name") == crop
    assert decision.parameters.get("district") == district.capitalize()
