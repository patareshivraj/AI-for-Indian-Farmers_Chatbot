from typing import Any, Dict
from datetime import datetime
from app.access.models import ToolName
from app.tools.base import BaseTool, ToolResult
from app.context.models import UserContext

class ChitChatTool(BaseTool):
    """Tool that handles general conversational queries (greetings, thanks) without hitting the database."""
    
    @property
    def tool_name(self) -> ToolName:
        return ToolName.CHITCHAT_TOOL
        
    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        """Returns a generic friendly payload for Groq to format."""
        return ToolResult(
            success=True,
            data={"system_note": "Acknowledge the user's conversational message politely. Remind them you are Farm360 Copilot, an AI designed to help with crops, schemes, land records, and farm queries."},
            message="Chit-chat response generated.",
            source="System",
            tool_name=self.tool_name,
            timestamp=datetime.utcnow()
        )
