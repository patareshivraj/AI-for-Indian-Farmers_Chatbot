from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext

class GetSoilHealthInfoTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_SOIL_HEALTH_INFO

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        self.validate_access(context, target_farmer_id=None)
        
        soil_type = kwargs.get("soil_type")

        try:
            query_str = "SELECT soil_type, characteristics, suitable_crops, improvement_methods FROM soil_health_awareness WHERE 1=1"
            params = {}
            if soil_type:
                query_str += " AND soil_type LIKE :soil_type"
                params["soil_type"] = f"%{soil_type}%"
                
            query = text(query_str)
            
            results = self.db_session.execute(query, params).mappings().fetchall()
            data = [dict(row) for row in results]
                
            return ToolResult(
                success=True,
                data=data,
                message=f"Retrieved {len(data)} soil health records",
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
