from app.context.models import Permissions, RoleEnum

class PermissionResolver:
    """Deterministic permission resolution based on role."""
    
    def get_permissions(self, role: RoleEnum) -> Permissions:
        """Returns standard permission flags for the given role."""
        
        if role == RoleEnum.FARMER:
            return Permissions(
                can_access_global_knowledge=True,
                can_access_market_prices=True,
                can_access_all_aggregates=False
            )
            
        elif role == RoleEnum.CONSULTANT:
            return Permissions(
                can_access_global_knowledge=True,
                can_access_market_prices=True,
                can_access_all_aggregates=False
            )
            
        elif role == RoleEnum.ADMIN:
            return Permissions(
                can_access_global_knowledge=True,
                can_access_market_prices=True,
                can_access_all_aggregates=True
            )
            
        # Fallback security
        return Permissions(
            can_access_global_knowledge=False,
            can_access_market_prices=False,
            can_access_all_aggregates=False
        )
