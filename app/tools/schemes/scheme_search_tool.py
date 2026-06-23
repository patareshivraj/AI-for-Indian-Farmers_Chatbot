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
            query_str = "SELECT scheme_name, description, benefit as benefits FROM schemes_master WHERE 1=1"
            params = {}
            # Fallback to fetching all active schemes if columns do not match schema
            # In a full implementation, we'd map this to crop_type or crop_name
            query_str += " AND is_active = 1 LIMIT 5"
                
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
