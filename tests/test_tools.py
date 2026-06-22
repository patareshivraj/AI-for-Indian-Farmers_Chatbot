import pytest
from unittest.mock import MagicMock
from app.context.models import (
    BaseUser, Permissions, FarmMetrics, FarmerContext, RoleEnum
)
from app.access.models import ToolName
from app.access.guard import ToolExecutionGuard
from app.tools.registry import ExecutableToolRegistry

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def mock_guard():
    guard = MagicMock(spec=ToolExecutionGuard)
    # validate() returns None if allowed, raises if not.
    guard.validate.return_value = None
    return guard

@pytest.fixture
def farmer_context():
    user = BaseUser(user_id=101, role=RoleEnum.FARMER, name="Rajesh", district="Pune")
    permissions = Permissions()
    metrics = FarmMetrics()
    return FarmerContext(user=user, permissions=permissions, farm_metrics=metrics)

@pytest.fixture
def tool_registry(mock_guard, mock_db_session):
    return ExecutableToolRegistry(guard=mock_guard, db_session=mock_db_session)

def test_get_my_profile_tool(tool_registry, mock_db_session, farmer_context):
    tool = tool_registry.get_tool(ToolName.GET_MY_PROFILE)
    
    # Mocking db returns
    mock_user_res = MagicMock()
    mock_user_res.mappings().first.return_value = {"name": "Rajesh", "state": "MH", "district": "Pune", "password": "hash"}
    
    mock_profile_res = MagicMock()
    mock_profile_res.mappings().first.return_value = {"language": "mr", "experience": 5}
    
    mock_db_session.execute.side_effect = [mock_user_res, mock_profile_res]
    
    result = tool.execute(farmer_context)
    
    assert result.success is True
    assert result.data["name"] == "Rajesh"
    assert "password" not in result.data
    assert result.tool_name == ToolName.GET_MY_PROFILE

def test_get_market_prices_tool(tool_registry, mock_db_session, farmer_context):
    tool = tool_registry.get_tool(ToolName.GET_MARKET_PRICES)
    
    mock_res = MagicMock()
    mock_res.mappings().fetchall.return_value = [
        {"market_name": "Pune APMC", "modal_price": 5000.0}
    ]
    mock_db_session.execute.return_value = mock_res
    
    result = tool.execute(farmer_context, crop_name="Cotton")
    
    assert result.success is True
    assert len(result.data) == 1
    assert result.data[0]["modal_price"] == 5000.0

def test_disease_tool(tool_registry, mock_db_session, farmer_context):
    tool = tool_registry.get_tool(ToolName.GET_DISEASE_INFO)
    
    mock_res = MagicMock()
    mock_res.mappings().fetchall.return_value = [
        {"disease_name": "Fusarium Wilt", "symptoms": "Yellowing of leaves"}
    ]
    mock_db_session.execute.return_value = mock_res
    
    result = tool.execute(farmer_context, disease_name="Wilt")
    
    assert result.success is True
    assert "Fusarium Wilt" in result.data[0]["disease_name"]

def test_scheme_search_tool(tool_registry, mock_db_session, farmer_context):
    tool = tool_registry.get_tool(ToolName.SEARCH_SCHEMES)
    
    mock_res = MagicMock()
    mock_res.mappings().fetchall.return_value = [
        {"scheme_name": "PM-KISAN", "benefits": "6000 per year"}
    ]
    mock_db_session.execute.return_value = mock_res
    
    result = tool.execute(farmer_context, state="Maharashtra")
    
    assert result.success is True
    assert len(result.data) == 1
    assert result.data[0]["scheme_name"] == "PM-KISAN"
