from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext
from app.core.security import sanitize_user_data

class GetMyProfileTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_MY_PROFILE

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        # Validate Access
        target_farmer_id = kwargs.get("target_farmer_id", context.user.user_id)
        self.validate_access(context, target_farmer_id)

        try:
            # Query User Master
            user_query = text("""
                SELECT u.full_name as name, s.state_name as state, d.district_name as district
                FROM user_master u
                LEFT JOIN state s ON u.state_id = s.state_id
                LEFT JOIN district d ON u.district_id = d.district_id
                WHERE u.user_id = :user_id
            """)
            
            # Query Farmer Profile
            profile_query = text("""
                SELECT preferred_language as language, farming_experience as experience
                FROM farmer_profile
                WHERE user_id = :user_id
            """)
            
            user_res = self.db_session.execute(user_query, {"user_id": target_farmer_id}).mappings().first()
            profile_res = self.db_session.execute(profile_query, {"user_id": target_farmer_id}).mappings().first()
            
            data = {}
            if user_res:
                data.update(dict(user_res))
            if profile_res:
                data.update(dict(profile_res))
                
            data = sanitize_user_data(data)
                
            return ToolResult(
                success=True,
                data=data,
                message="Profile retrieved successfully",
                source="database",
                tool_name=self.tool_name,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            return ToolResult(
                success=False,
                message=str(e),
                source="database",
                tool_name=self.tool_name,
                timestamp=datetime.utcnow()
            )
