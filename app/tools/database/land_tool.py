from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext
from app.core.security import sanitize_land_record

class GetMyLandRecordsTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_MY_LAND_RECORDS

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        target_farmer_id = kwargs.get("target_farmer_id", context.user.user_id)
        self.validate_access(context, target_farmer_id)

        try:
            query = text("""
                SELECT id as record_id, land_area, farm_name, survey_number
                FROM farmer_land_records
                WHERE farmer_id = :user_id
            """)
            
            results = self.db_session.execute(query, {"user_id": target_farmer_id}).mappings().fetchall()
            data = [sanitize_land_record(dict(row)) for row in results]
                
            return ToolResult(
                success=True,
                data=data,
                message=f"Retrieved {len(data)} land records",
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
