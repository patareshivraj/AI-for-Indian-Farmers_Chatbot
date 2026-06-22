from app.router.models import RoutingDecision
from app.router.classifier import IntentClassifier
from app.router.extractor import ParameterExtractor
from app.router.resolver import ToolResolver
from app.router.confidence import ConfidenceScorer

class QueryRouter:
    """The central brain orchestrating classification, extraction, and resolution."""
    
    def __init__(self):
        self.classifier = IntentClassifier()
        self.extractor = ParameterExtractor()
        self.resolver = ToolResolver()
        self.scorer = ConfidenceScorer()

    def route(self, question: str) -> RoutingDecision:
        """
        Processes a natural language query and returns an executable routing decision.
        """
        # 1. Classify Intent
        raw_intent = self.classifier.classify(question)
        
        # 2. Score and Adjust Confidence
        scored_intent = self.scorer.score(raw_intent)
        
        # 3. Extract Parameters
        params = self.extractor.extract(question)
        
        # 4. Resolve Tool
        tool_name = self.resolver.resolve(scored_intent.intent)
        
        # Build routing decision
        decision = RoutingDecision(
            intent=scored_intent.intent,
            tool_name=tool_name,
            parameters=params,
            confidence=scored_intent.confidence
        )
        
        return decision
