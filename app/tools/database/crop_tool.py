from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext

class GetMyActiveCropsTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_MY_ACTIVE_CROPS

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        target_farmer_id = kwargs.get("target_farmer_id", context.user.user_id)
        self.validate_access(context, target_farmer_id)

        try:
            query = text("""
                SELECT id as crop_record_id, crop_name, date_of_sowing, expected_harvest_date, land_id
                FROM farmer_crop_details
                WHERE farmer_id = :user_id AND is_crop_planted = 1
            """)
            
            results = self.db_session.execute(query, {"user_id": str(target_farmer_id)}).mappings().fetchall()
            crops = [dict(row) for row in results]
                
            return ToolResult(
                success=True,
                data={
                    "crop_count": len(crops),
                    "crops": crops
                },
                message=f"Retrieved {len(crops)} active crops",
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
