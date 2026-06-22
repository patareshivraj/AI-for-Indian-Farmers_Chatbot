import uuid
from typing import Optional
from app.router.models import RoutingDecision
from app.execution.models import ExecutionResult
from app.memory.persistence import MemoryPersistence
from app.memory.session_store import SessionStore
from app.memory.entity_tracker import EntityTracker
from app.memory.state_resolver import StateResolver
from app.memory.context_enricher import ContextEnricher
from app.memory.models import ConversationState

class MemoryManager:
    """Master orchestration layer for conversation memory."""
    
    def __init__(self, persistence: MemoryPersistence):
        self.session_store = SessionStore(persistence)
        self.entity_tracker = EntityTracker(persistence)
        
    def enrich_decision(self, session_id: str, user_id: int, original_query: str, decision: RoutingDecision) -> RoutingDecision:
        """
        Takes the initial routing decision. If it requires memory context,
        loads state and entities, and enriches the decision parameters.
        """
        # Cleanup expired memory occasionally
        self.session_store.clean_expired()
        self.entity_tracker.clean_expired()
        
        if not StateResolver.requires_memory(original_query, decision):
            return decision
            
        state = self.session_store.get_session(session_id, user_id)
        entities = self.entity_tracker.get_entities(session_id, user_id)
        
        return ContextEnricher.enrich(decision, state, entities)

    def post_execution_update(self, session_id: str, user_id: int, decision: RoutingDecision, result: ExecutionResult) -> None:
        """
        Updates session state and tracked entities ONLY IF execution was successful.
        """
        if not result.success:
            return
            
        # 1. Update Session State
        state = ConversationState(
            session_id=session_id,
            user_id=user_id,
            active_intent=decision.intent,
            active_tool=decision.tool_name,
            last_parameters=decision.parameters
        )
        self.session_store.update_session(state)
        
        # 2. Update Tracked Entities
        self.entity_tracker.update_entities(session_id, user_id, decision.parameters)
