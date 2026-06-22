from app.router.intents import Intent
from app.router.models import IntentResult

class ConfidenceScorer:
    """Evaluates and adjusts confidence scores."""

    def score(self, intent_result: IntentResult) -> IntentResult:
        """
        Applies confidence thresholds.
        >= 0.85: High
        0.60 - 0.84: Medium
        < 0.60: Low (Routes to UNKNOWN)
        """
        if intent_result.confidence < 0.60:
            return IntentResult(
                intent=Intent.UNKNOWN,
                confidence=intent_result.confidence,
                reason="Confidence below minimum threshold. Routing to UNKNOWN."
            )
            
        return intent_result
