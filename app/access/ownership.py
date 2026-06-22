from typing import Optional
from app.access.models import ToolAccessProfile
from app.context.models import RoleEnum

class OwnershipValidator:
    """Primary anti-data-leak mechanism verifying ID bounds."""

    def validate(self, profile: ToolAccessProfile, target_farmer_id: Optional[int]) -> bool:
        """
        Verifies if the current user profile is allowed to access the target_farmer_id.
        Admins bypass farmer_id bounds.
        """
        if target_farmer_id is None:
            return True
            
        if profile.role == RoleEnum.ADMIN:
            return True
            
        return target_farmer_id in profile.accessible_farmer_ids
