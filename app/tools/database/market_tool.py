from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext

class GetMarketPricesTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_MARKET_PRICES

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        self.validate_access(context, target_farmer_id=None)
        
        crop_name = kwargs.get("crop_name")
        district = kwargs.get("district", context.user.district)

        try:
            query = text("""
                SELECT mp.market_name, cp.min_price, cp.max_price, cp.modal_price, cp.arrival_date
                FROM commodity_price cp
                JOIN market_prices mp ON cp.market_id = mp.id
                WHERE cp.commodity_name = :crop_name AND mp.district = :district
                ORDER BY cp.arrival_date DESC
                LIMIT 5
            """)
            
            results = self.db_session.execute(query, {"crop_name": crop_name, "district": district}).mappings().fetchall()
            prices = [dict(row) for row in results]
                
            return ToolResult(
                success=True,
                data=prices,
                message=f"Retrieved {len(prices)} market price records",
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
