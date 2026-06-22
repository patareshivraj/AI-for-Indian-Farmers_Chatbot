from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext

class GetFarmingTipsTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_FARMING_TIPS

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        self.validate_access(context, target_farmer_id=None)
        
        crop_name = kwargs.get("crop_name")
        month = kwargs.get("month")

        try:
            # 1. Get Daily Farming Tips
            tips_query = text("SELECT tip_content, category FROM daily_farming_tips ORDER BY published_date DESC LIMIT 5")
            tips_results = self.db_session.execute(tips_query).mappings().fetchall()
            
            # 2. Get Crop Calendar
            cal_query_str = "SELECT crop_name, sowing_month, harvesting_month, activities FROM crop_calendar WHERE 1=1"
            params = {}
            if crop_name:
                cal_query_str += " AND crop_name LIKE :crop_name"
                params["crop_name"] = f"%{crop_name}%"
            if month:
                cal_query_str += " AND (sowing_month = :month OR harvesting_month = :month)"
                params["month"] = month
                
            cal_query = text(cal_query_str)
            cal_results = self.db_session.execute(cal_query, params).mappings().fetchall()
            
            data = {
                "daily_tips": [dict(row) for row in tips_results],
                "crop_calendar": [dict(row) for row in cal_results]
            }
                
            return ToolResult(
                success=True,
                data=data,
                message="Retrieved farming tips and calendar successfully",
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
