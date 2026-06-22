from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext

class SchemeSearchTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.SEARCH_SCHEMES

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        self.validate_access(context, target_farmer_id=None)
        
        state = kwargs.get("state")
        category = kwargs.get("category")

        try:
            query_str = "SELECT scheme_name, description, eligibility_criteria, benefits FROM schemes_master WHERE 1=1"
            params = {}
            if state:
                query_str += " AND applicable_state LIKE :state"
                params["state"] = f"%{state}%"
            if category:
                query_str += " AND category LIKE :category"
                params["category"] = f"%{category}%"
                
            query = text(query_str)
            
            results = self.db_session.execute(query, params).mappings().fetchall()
            data = [dict(row) for row in results]
                
            return ToolResult(
                success=True,
                data=data,
                message=f"Retrieved {len(data)} schemes",
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
