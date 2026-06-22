import pytest
from datetime import datetime, timedelta
from app.router.intents import Intent
from app.access.models import ToolName
from app.router.models import RoutingDecision
from app.execution.models import ExecutionResult
from app.memory.models import ConversationState, TrackedEntities
from app.memory.security import MemorySecurityValidator
from app.memory.persistence import MemoryPersistence, Base, ConversationMemoryModel
from app.memory.session_store import SessionStore
from app.memory.entity_tracker import EntityTracker
from app.memory.state_resolver import StateResolver
from app.memory.context_enricher import ContextEnricher
from app.memory.memory_manager import MemoryManager
from app.core.exceptions import MemorySecurityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

@pytest.fixture
def persistence(db_session):
    return MemoryPersistence(db_session)

@pytest.fixture
def memory_manager(persistence):
    return MemoryManager(persistence)

def test_memory_security_validator_blocks_pii():
    with pytest.raises(MemorySecurityError):
        MemorySecurityValidator.validate({"adhar": "123456789012"})
    
    with pytest.raises(MemorySecurityError):
        MemorySecurityValidator.validate({"password": "my_password"})

    # Content scan check
    with pytest.raises(MemorySecurityError):
        MemorySecurityValidator.validate({"user_aadhar_value": "123456789012"})

def test_memory_security_validator_allows_safe_data():
    MemorySecurityValidator.validate({"crop_name": "soybean", "district": "pune"})

def test_session_store_crud(persistence):
    store = SessionStore(persistence)
    state = ConversationState(session_id="s1", user_id=1, active_intent=Intent.CROP_QUERY, active_tool=ToolName.GET_MY_ACTIVE_CROPS)
    store.update_session(state)
    
    loaded = store.get_session("s1", 1)
    assert loaded is not None
    assert loaded.active_intent == Intent.CROP_QUERY

def test_entity_tracker_updates(persistence):
    tracker = EntityTracker(persistence)
    tracker.update_entities("s1", 1, {"crop_name": "soybean", "random_stuff": "ignore"})
    
    entities = tracker.get_entities("s1", 1)
    assert entities.crop_name == "soybean"
    assert not hasattr(entities, "random_stuff")

def test_state_resolver_requires_memory():
    decision = RoutingDecision(intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, parameters={"district": "pune"}, confidence=0.9)
    assert StateResolver.requires_memory("what about nashik?", decision) is True
    
    decision_full = RoutingDecision(intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, parameters={"crop_name": "cotton", "district": "pune"}, confidence=0.9)
    # Even if full, "what about" triggers memory
    assert StateResolver.requires_memory("what about nashik?", decision_full) is True
    
    # Independent query
    decision_indep = RoutingDecision(intent=Intent.PROFILE_QUERY, tool_name=ToolName.GET_MY_PROFILE, parameters={}, confidence=0.9)
    assert StateResolver.requires_memory("Show my profile", decision_indep) is False

def test_context_enrichment():
    decision = RoutingDecision(intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, parameters={"district": "Nashik"}, confidence=0.9)
    state = ConversationState(session_id="s1", user_id=1, active_intent=Intent.MARKET_QUERY, active_tool=ToolName.GET_MARKET_PRICES)
    entities = TrackedEntities(crop_name="soybean", district="Pune")
    
    enriched = ContextEnricher.enrich(decision, state, entities)
    assert enriched.parameters["district"] == "Nashik" # Query overrides entity
    assert enriched.parameters["crop_name"] == "soybean" # Entity backfills query

def test_memory_manager_post_execution(memory_manager):
    decision = RoutingDecision(intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, parameters={"crop_name": "cotton", "district": "pune"}, confidence=0.9)
    result = ExecutionResult(success=True, intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, data={"prices": 100}, execution_time_ms=10)
    
    memory_manager.post_execution_update("s1", 1, decision, result)
    
    # Check session
    session = memory_manager.session_store.get_session("s1", 1)
    assert session.active_intent == Intent.MARKET_QUERY
    assert session.last_parameters == {"crop_name": "cotton", "district": "pune"}
    
    # Check entities
    entities = memory_manager.entity_tracker.get_entities("s1", 1)
    assert entities.crop_name == "cotton"
    assert entities.district == "pune"

def test_memory_manager_failed_execution_no_update(memory_manager):
    decision = RoutingDecision(intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, parameters={"crop_name": "cotton"}, confidence=0.9)
    result = ExecutionResult(success=False, intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, error="Failed", execution_time_ms=0)
    
    memory_manager.post_execution_update("s2", 2, decision, result)
    
    session = memory_manager.session_store.get_session("s2", 2)
    assert session is None

def test_memory_expiration(persistence, db_session):
    store = SessionStore(persistence)
    state = ConversationState(session_id="s1", user_id=1)
    store.update_session(state)
    
    # Manually backdate updated_at
    record = db_session.query(ConversationMemoryModel).first()
    record.updated_at = datetime.utcnow() - timedelta(minutes=60)
    db_session.commit()
    
    store.clean_expired()
    assert store.get_session("s1", 1) is None
