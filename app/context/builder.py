from typing import Union
from app.core.exceptions import ContextBuilderError, UserNotFoundError, InvalidRoleError
from app.core.cache import context_cache
from app.context.models import (
    RoleEnum, LanguageEnum, BaseUser, 
    FarmerContext, ConsultantContext, AdminContext,
    FarmMetrics, ConsultantAssignments
)
from app.context.role_resolver import RoleResolver
from app.context.permissions import PermissionResolver
from app.repositories.user_repo import UserRepository
from app.repositories.farmer_repo import FarmerRepository
from app.repositories.consultant_repo import ConsultantRepository

class ContextBuilder:
    """Orchestrates the construction of deterministic, typed Context objects."""
    
    def __init__(
        self, 
        user_repo: UserRepository, 
        farmer_repo: FarmerRepository, 
        consultant_repo: ConsultantRepository
    ):
        self.user_repo = user_repo
        self.farmer_repo = farmer_repo
        self.consultant_repo = consultant_repo
        self.role_resolver = RoleResolver(user_repo)
        self.permission_resolver = PermissionResolver()
        
    def build_context(self, user_id: int, use_cache: bool = True) -> Union[FarmerContext, ConsultantContext, AdminContext]:
        """
        Builds the complete Context object for a given user.
        Uses TTL caching to avoid repeated database hits.
        """
        cache_key = f"context_{user_id}"
        
        if use_cache:
            cached = context_cache.get(cache_key)
            if cached:
                return cached
                
        try:
            # 1. Resolve Role
            role = self.role_resolver.resolve(user_id)
            
            # 2. Get User Base Data
            user_data = self.user_repo.get_user_by_id(user_id)
            if not user_data:
                raise UserNotFoundError(f"User {user_id} not found after resolving role.")
                
            # Map language string to LanguageEnum safely
            lang_str = user_data.get("language", "en").lower()
            try:
                language = LanguageEnum(lang_str)
            except ValueError:
                language = LanguageEnum.OTHER
                
            base_user = BaseUser(
                user_id=user_id,
                role=role,
                name=user_data.get("name", ""),
                mobile_number=user_data.get("mobile_number"),
                state=user_data.get("state"),
                district=user_data.get("district"),
                language=language
            )
            
            # 3. Resolve Permissions
            permissions = self.permission_resolver.get_permissions(role)
            
            # 4. Build Role-Specific Context
            if role == RoleEnum.FARMER:
                metrics_data = self.farmer_repo.get_farm_metrics(user_id)
                farm_metrics = FarmMetrics(**metrics_data)
                
                context = FarmerContext(
                    user=base_user,
                    permissions=permissions,
                    farm_metrics=farm_metrics
                )
                
            elif role == RoleEnum.CONSULTANT:
                farmer_ids = self.consultant_repo.get_authorized_farmers(user_id)
                assignments = ConsultantAssignments(authorized_farmer_ids=farmer_ids)
                
                context = ConsultantContext(
                    user=base_user,
                    permissions=permissions,
                    assignments=assignments
                )
                
            elif role == RoleEnum.ADMIN:
                context = AdminContext(
                    user=base_user,
                    permissions=permissions
                )
                
            else:
                raise InvalidRoleError(f"Unhandled role type: {role}")
                
            # Store in cache
            if use_cache:
                context_cache.set(cache_key, context)
                
            return context
            
        except (UserNotFoundError, InvalidRoleError):
            raise
        except Exception as e:
            raise ContextBuilderError(f"Failed to build context for user {user_id}: {str(e)}")
