from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext

class GetMyInventoryTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_MY_INVENTORY

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        target_farmer_id = kwargs.get("target_farmer_id", context.user.user_id)
        self.validate_access(context, target_farmer_id)

        try:
            query = text("""
                SELECT item_name, item_category, quantity, unit, last_updated
                FROM farmer_instock
                WHERE farmer_id = :user_id
            """)
            
            results = self.db_session.execute(query, {"user_id": target_farmer_id}).mappings().fetchall()
            inventory = [dict(row) for row in results]
                
            return ToolResult(
                success=True,
                data=inventory,
                message=f"Retrieved {len(inventory)} inventory items",
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
