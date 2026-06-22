from typing import Optional
from app.router.models import RoutingDecision
from app.memory.models import ConversationState, TrackedEntities

class ContextEnricher:
    """Merges current routing decision with memory context."""

    @classmethod
    def enrich(cls, decision: RoutingDecision, state: Optional[ConversationState], entities: TrackedEntities) -> RoutingDecision:
        """
        Enriches the decision parameters with data from memory.
        If a parameter is missing in the current query, we backfill it from entities.
        If the tool is missing, we might backfill it from state.
        """
        enriched_params = dict(decision.parameters)
        
        # Merge missing parameters from entities
        entity_dict = entities.model_dump(exclude_none=True)
        for key, value in entity_dict.items():
            if key not in enriched_params or not enriched_params[key]:
                enriched_params[key] = value

        # If the intent is inherited from last conversation turn
        # e.g. User: "What about Nashik?" -> Intent is UNKNOWN or MARKET_QUERY
        # If router gave MARKET_QUERY but it had no crop, we just filled the crop above.
        
        # Return a new enriched decision
        return RoutingDecision(
            intent=decision.intent,
            tool_name=decision.tool_name or (state.active_tool if state else None),
            parameters=enriched_params,
            confidence=decision.confidence
        )
