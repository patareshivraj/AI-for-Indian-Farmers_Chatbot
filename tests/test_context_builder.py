import pytest
from unittest.mock import MagicMock
from app.context.builder import ContextBuilder
from app.context.models import RoleEnum, FarmerContext, ConsultantContext, AdminContext
from app.core.exceptions import UserNotFoundError, InvalidRoleError

@pytest.fixture
def mock_repos():
    user_repo = MagicMock()
    farmer_repo = MagicMock()
    consultant_repo = MagicMock()
    return user_repo, farmer_repo, consultant_repo

@pytest.fixture
def builder(mock_repos):
    user_repo, farmer_repo, consultant_repo = mock_repos
    return ContextBuilder(user_repo, farmer_repo, consultant_repo)

def test_valid_farmer_context(builder, mock_repos):
    user_repo, farmer_repo, _ = mock_repos
    
    # Mock user repository
    user_repo.get_user_by_id.return_value = {
        "user_id": 101,
        "role_id": 2, # Farmer
        "name": "Rajesh",
        "language": "mr",
        "state": "Maharashtra",
        "district": "Pune"
    }
    
    # Mock farmer repository
    farmer_repo.get_farm_metrics.return_value = {
        "total_land_area_acres": 12.5,
        "active_land_count": 2,
        "active_crops": ["Wheat", "Sugarcane"],
        "land_ids": [1, 2]
    }
    
    context = builder.build_context(101, use_cache=False)
    
    assert isinstance(context, FarmerContext)
    assert context.user.role == RoleEnum.FARMER
    assert context.farm_metrics.total_land_area_acres == 12.5
    assert "Wheat" in context.farm_metrics.active_crops
    assert context.permissions.can_access_global_knowledge is True

def test_valid_consultant_context(builder, mock_repos):
    user_repo, _, consultant_repo = mock_repos
    
    user_repo.get_user_by_id.return_value = {
        "user_id": 201,
        "role_id": 3, # Consultant
        "name": "Dr. Sharma",
        "language": "en"
    }
    
    consultant_repo.get_authorized_farmers.return_value = [101, 102]
    
    context = builder.build_context(201, use_cache=False)
    
    assert isinstance(context, ConsultantContext)
    assert context.user.role == RoleEnum.CONSULTANT
    assert 101 in context.assignments.authorized_farmer_ids

def test_valid_admin_context(builder, mock_repos):
    user_repo, _, _ = mock_repos
    
    user_repo.get_user_by_id.return_value = {
        "user_id": 1,
        "role_id": 1, # Admin
        "name": "Super Admin"
    }
    
    context = builder.build_context(1, use_cache=False)
    
    assert isinstance(context, AdminContext)
    assert context.user.role == RoleEnum.ADMIN
    assert context.permissions.can_access_all_aggregates is True

def test_invalid_user(builder, mock_repos):
    user_repo, _, _ = mock_repos
    user_repo.get_user_by_id.return_value = None
    
    with pytest.raises(UserNotFoundError):
        builder.build_context(999, use_cache=False)

def test_invalid_role(builder, mock_repos):
    user_repo, _, _ = mock_repos
    user_repo.get_user_by_id.return_value = {
        "user_id": 105,
        "role_id": 99 # Unknown
    }
    
    with pytest.raises(InvalidRoleError):
        builder.build_context(105, use_cache=False)

def test_missing_profile_graceful_fallback(builder, mock_repos):
    user_repo, farmer_repo, _ = mock_repos
    
    user_repo.get_user_by_id.return_value = {
        "user_id": 102,
        "role_id": 2
    }
    
    # Missing profile returns empty/defaults
    farmer_repo.get_farm_metrics.return_value = {
        "total_land_area_acres": 0.0,
        "active_land_count": 0,
        "active_crops": [],
        "land_ids": []
    }
    
    context = builder.build_context(102, use_cache=False)
    assert context.farm_metrics.total_land_area_acres == 0.0

def test_empty_assignments(builder, mock_repos):
    user_repo, _, consultant_repo = mock_repos
    
    user_repo.get_user_by_id.return_value = {
        "user_id": 202,
        "role_id": 3
    }
    
    consultant_repo.get_authorized_farmers.return_value = []
    
    context = builder.build_context(202, use_cache=False)
    assert len(context.assignments.authorized_farmer_ids) == 0
