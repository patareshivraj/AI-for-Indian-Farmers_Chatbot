from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext

class GetPestInfoTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_PEST_INFO

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        self.validate_access(context, target_farmer_id=None)
        
        pest_name = kwargs.get("pest_name")
        crop_name = kwargs.get("crop_name")

        try:
            query_str = "SELECT pest_name, damage_symptoms, control_measures FROM pest_awareness WHERE 1=1"
            params = {}
            if pest_name:
                query_str += " AND pest_name LIKE :pest_name"
                params["pest_name"] = f"%{pest_name}%"
            if crop_name:
                query_str += " AND target_crops LIKE :crop_name"
                params["crop_name"] = f"%{crop_name}%"
                
            query = text(query_str)
            
            results = self.db_session.execute(query, params).mappings().fetchall()
            data = [dict(row) for row in results]
                
            return ToolResult(
                success=True,
                data=data,
                message=f"Retrieved {len(data)} pest records",
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
