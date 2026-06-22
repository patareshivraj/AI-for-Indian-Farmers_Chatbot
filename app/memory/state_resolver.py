from app.router.models import RoutingDecision

class StateResolver:
    """Determines if a RoutingDecision needs context enrichment."""
    
    # Pronouns or continuation indicators that might suggest memory dependency
    CONTINUATION_TOKENS = {
        "what about", "how about", "and", "latest", "previous", "them", "it", "more"
    }

    @classmethod
    def requires_memory(cls, original_query: str, decision: RoutingDecision) -> bool:
        """
        Returns True if the current query seems dependent on previous context.
        """
        # 1. If intent is UNKNOWN, we don't attempt memory resolution. Let it fail normally.
        if decision.intent.value == "UNKNOWN":
            return False
            
        # 2. If it has all the parameters it needs, it likely doesn't need memory.
        # (Router usually drops parameters if they aren't explicitly mentioned).
        # We will check if it's missing parameters it normally requires, but the easiest heuristic 
        # is looking for continuation tokens in the raw text.
        normalized = original_query.lower()
        
        for token in cls.CONTINUATION_TOKENS:
            if token in normalized:
                return True
                
        # 3. Parameter-based inference: If they are asking for market prices but didn't provide a crop,
        # they probably meant the active crop.
        if decision.intent.value == "MARKET_QUERY" and not decision.parameters.get("crop_name"):
            return True
            
        if decision.intent.value == "PEST_QUERY" and not decision.parameters.get("pest_name") and not decision.parameters.get("crop_name"):
            return True
            
        if decision.intent.value == "SCHEME_QUERY" and not decision.parameters:
            return True

        return False
