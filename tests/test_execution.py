import pytest
from unittest.mock import MagicMock
from app.router.intents import Intent
from app.router.models import RoutingDecision
from app.access.models import ToolName
from app.execution.models import ExecutionPlan
from app.execution.agents.database_agent import DatabaseAgent
from app.execution.agents.knowledge_agent import KnowledgeAgent
from app.execution.agents.scheme_agent import SchemeAgent
from app.execution.resolver import AgentResolver
from app.execution.planner import ExecutionPlanner
from app.execution.executor import ExecutionEngine
from app.execution.orchestrator import Farm360Orchestrator

@pytest.fixture
def mock_tool_registry():
    registry = MagicMock()
    # Mock tool execution
    mock_tool = MagicMock()
    mock_tool.execute.return_value = MagicMock(success=True, data={"result": "data"}, message="Success")
    registry.get_tool.return_value = mock_tool
    return registry

@pytest.fixture
def agents(mock_tool_registry):
    return [
        DatabaseAgent(mock_tool_registry),
        KnowledgeAgent(mock_tool_registry),
        SchemeAgent(mock_tool_registry)
    ]

@pytest.fixture
def agent_resolver(agents):
    return AgentResolver(agents)

@pytest.fixture
def engine(agent_resolver):
    return ExecutionEngine(agent_resolver)

def test_database_agent_handles_correct_intents(mock_tool_registry):
    agent = DatabaseAgent(mock_tool_registry)
    assert agent.can_handle(Intent.CROP_QUERY) is True
    assert agent.can_handle(Intent.MARKET_QUERY) is True
    assert agent.can_handle(Intent.PEST_QUERY) is False

def test_knowledge_agent_handles_correct_intents(mock_tool_registry):
    agent = KnowledgeAgent(mock_tool_registry)
    assert agent.can_handle(Intent.PEST_QUERY) is True
    assert agent.can_handle(Intent.DISEASE_QUERY) is True
    assert agent.can_handle(Intent.SCHEME_QUERY) is False

def test_scheme_agent_handles_correct_intents(mock_tool_registry):
    agent = SchemeAgent(mock_tool_registry)
    assert agent.can_handle(Intent.SCHEME_QUERY) is True
    assert agent.can_handle(Intent.CROP_QUERY) is False

def test_agent_resolver(agent_resolver):
    assert isinstance(agent_resolver.resolve(Intent.CROP_QUERY), DatabaseAgent)
    assert isinstance(agent_resolver.resolve(Intent.PEST_QUERY), KnowledgeAgent)
    assert isinstance(agent_resolver.resolve(Intent.SCHEME_QUERY), SchemeAgent)
    assert agent_resolver.resolve(Intent.UNKNOWN) is None

def test_execution_planner():
    planner = ExecutionPlanner()
    decision = RoutingDecision(
        intent=Intent.CROP_QUERY,
        tool_name=ToolName.GET_MY_ACTIVE_CROPS,
        parameters={"test": "123"},
        confidence=0.9
    )
    plans = planner.create_plan(decision)
    assert len(plans) == 1
    assert plans[0].tool_name == ToolName.GET_MY_ACTIVE_CROPS
    assert plans[0].parameters == {"test": "123"}

def test_execution_engine(engine):
    plan = ExecutionPlan(
        intent=Intent.CROP_QUERY,
        tool_name=ToolName.GET_MY_ACTIVE_CROPS,
        parameters={}
    )
    context = MagicMock()
    
    results = engine.execute([plan], context)
    assert len(results) == 1
    assert results[0].success is True
    assert results[0].data == {"result": "data"}
    assert len(engine.traces) == 1
    assert engine.traces[0].agent_name == "DatabaseAgent"

def test_orchestrator(mock_tool_registry, engine):
    # Setup mocks
    mock_context_builder = MagicMock()
    mock_context_builder.build.return_value = MagicMock()
    
    mock_router = MagicMock()
    mock_router.route.return_value = RoutingDecision(
        intent=Intent.CROP_QUERY,
        tool_name=ToolName.GET_MY_ACTIVE_CROPS,
        parameters={},
        confidence=0.9
    )
    
    planner = ExecutionPlanner()
    
    orchestrator = Farm360Orchestrator(
        context_builder=mock_context_builder,
        query_router=mock_router,
        execution_planner=planner,
        execution_engine=engine
    )
    
    result = orchestrator.run(user_id=101, question="What crops do I have?")
    assert result.success is True
    assert result.data == {"result": "data"}
    assert result.intent == Intent.CROP_QUERY
    assert result.tool_name == ToolName.GET_MY_ACTIVE_CROPS

def test_orchestrator_unknown_query(mock_tool_registry, engine):
    mock_context_builder = MagicMock()
    mock_router = MagicMock()
    mock_router.route.return_value = RoutingDecision(
        intent=Intent.UNKNOWN,
        tool_name=None,
        parameters={},
        confidence=0.1
    )
    planner = ExecutionPlanner()
    
    orchestrator = Farm360Orchestrator(
        context_builder=mock_context_builder,
        query_router=mock_router,
        execution_planner=planner,
        execution_engine=engine
    )
    
    result = orchestrator.run(user_id=101, question="Explain quantum mechanics")
    assert result.success is False
    assert result.tool_name is None
    assert result.error == "Query not understood or unsupported."
