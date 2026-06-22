from app.context.models import RoleEnum
from app.core.exceptions import InvalidRoleError, UserNotFoundError
from app.repositories.user_repo import UserRepository

class RoleResolver:
    """Resolves a user ID to a strict RoleEnum based on database definitions."""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        
    def resolve(self, user_id: int) -> RoleEnum:
        """
        Retrieves user from database and maps their role ID to RoleEnum.
        Raises UserNotFoundError or InvalidRoleError.
        """
        user_data = self.user_repo.get_user_by_id(user_id)
        if not user_data:
            raise UserNotFoundError(f"User with ID {user_id} not found.")
            
        role_id = user_data.get("role_id")
        
        # Mapping based on typical farm360 role assumptions (adjust based on actual schema data if needed)
        # 1: ADMIN, 2: FARMER, 3: CONSULTANT
        if role_id == 1:
            return RoleEnum.ADMIN
        elif role_id == 2:
            return RoleEnum.FARMER
        elif role_id == 3:
            return RoleEnum.CONSULTANT
        else:
            raise InvalidRoleError(f"Role ID {role_id} is not mapped to any valid RoleEnum.")
