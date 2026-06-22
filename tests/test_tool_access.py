import pytest
from app.context.models import (
    BaseUser, Permissions, FarmMetrics, ConsultantAssignments,
    FarmerContext, ConsultantContext, AdminContext, RoleEnum
)
from app.access.models import ToolName
from app.access.guard import ToolExecutionGuard
from app.core.exceptions import AccessDeniedError

@pytest.fixture
def farmer_context():
    user = BaseUser(user_id=101, role=RoleEnum.FARMER, name="Rajesh")
    permissions = Permissions()
    metrics = FarmMetrics()
    return FarmerContext(user=user, permissions=permissions, farm_metrics=metrics)

@pytest.fixture
def consultant_context():
    user = BaseUser(user_id=205, role=RoleEnum.CONSULTANT, name="Dr. Sharma")
    permissions = Permissions()
    assignments = ConsultantAssignments(authorized_farmer_ids=[101, 102, 103])
    return ConsultantContext(user=user, permissions=permissions, assignments=assignments)

@pytest.fixture
def admin_context():
    user = BaseUser(user_id=1, role=RoleEnum.ADMIN, name="Super Admin")
    permissions = Permissions(can_access_all_aggregates=True)
    return AdminContext(user=user, permissions=permissions)

@pytest.fixture
def guard():
    return ToolExecutionGuard()

def test_farmer_access_allowed(guard, farmer_context):
    # Farmer accessing their own profile
    guard.validate(farmer_context, ToolName.GET_MY_PROFILE, target_farmer_id=101)
    
def test_farmer_access_unauthorized_tool(guard, farmer_context):
    # Farmer attempting to access analytics
    with pytest.raises(AccessDeniedError):
        guard.validate(farmer_context, ToolName.GET_PLATFORM_STATISTICS)

def test_farmer_access_another_farmer(guard, farmer_context):
    # Farmer attempting to access another farmer's data
    with pytest.raises(AccessDeniedError):
        guard.validate(farmer_context, ToolName.GET_MY_PROFILE, target_farmer_id=102)

def test_consultant_access_allowed(guard, consultant_context):
    # Consultant accessing an assigned farmer
    guard.validate(consultant_context, ToolName.GET_ASSIGNED_FARMER_SUMMARY, target_farmer_id=101)

def test_consultant_access_unassigned_farmer(guard, consultant_context):
    # Consultant accessing an unassigned farmer
    with pytest.raises(AccessDeniedError):
        guard.validate(consultant_context, ToolName.GET_ASSIGNED_FARMER_SUMMARY, target_farmer_id=999)

def test_consultant_unauthorized_tool(guard, consultant_context):
    # Consultant attempting to access analytics
    with pytest.raises(AccessDeniedError):
        guard.validate(consultant_context, ToolName.GET_PLATFORM_STATISTICS)

def test_admin_access_allowed(guard, admin_context):
    # Admin accessing platform statistics
    guard.validate(admin_context, ToolName.GET_PLATFORM_STATISTICS)
    
def test_admin_access_any_farmer():
    from app.access.ownership import OwnershipValidator
    from app.access.models import ToolAccessProfile
    # Admin accessing a specific farmer (bypasses ownership check)
    validator = OwnershipValidator()
    profile = ToolAccessProfile(
        role=RoleEnum.ADMIN,
        allowed_tools=[],
        blocked_tools=[],
        accessible_farmer_ids=[],
        can_access_global_knowledge=True,
        can_access_market_data=True,
        can_access_platform_analytics=True
    )
    assert validator.validate(profile, target_farmer_id=101) is True

def test_tool_registry_metadata():
    from app.access.registry import ToolRegistry
    # Verify metadata exists for a tool
    metadata = ToolRegistry.get_metadata(ToolName.GET_MY_PROFILE)
    assert metadata.requires_farmer_context is True
