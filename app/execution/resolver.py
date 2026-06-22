from typing import List, Optional
from app.execution.agents.base import BaseAgent
from app.router.intents import Intent

class AgentResolver:
    """Maps an intent to the correct registered Agent."""

    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def resolve(self, intent: Intent) -> Optional[BaseAgent]:
        for agent in self.agents:
            if agent.can_handle(intent):
                return agent
        return None
