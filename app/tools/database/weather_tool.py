from datetime import datetime
from sqlalchemy import text
from app.tools.base import BaseTool, ToolResult
from app.access.models import ToolName
from app.context.models import UserContext

class GetWeatherTool(BaseTool):
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.GET_WEATHER

    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        self.validate_access(context, target_farmer_id=None)
        
        district = kwargs.get("district", context.user.district)

        try:
            query = text("""
                SELECT current_temp, forecast, humidity, wind_speed, recorded_at
                FROM weather_snapshots
                WHERE district = :district
                ORDER BY recorded_at DESC
                LIMIT 1
            """)
            
            alert_query = text("""
                SELECT alert_message, severity
                FROM weather_awareness
                WHERE district = :district AND is_active = 1
            """)
            
            weather = self.db_session.execute(query, {"district": district}).mappings().first()
            alerts = self.db_session.execute(alert_query, {"district": district}).mappings().fetchall()
            
            data = {
                "latest_weather": dict(weather) if weather else None,
                "alerts": [dict(a) for a in alerts]
            }
                
            return ToolResult(
                success=True,
                data=data,
                message="Weather retrieved successfully",
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
