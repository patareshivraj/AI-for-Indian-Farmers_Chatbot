import re
from typing import List, Tuple
from app.router.intents import Intent
from app.router.models import IntentResult

class IntentClassifier:
    """Classifies natural language text into deterministic Intents using rule-based and semantic matching."""

    def __init__(self):
        # Multilingual keyword mappings (English, Hindi, Marathi)
        self.intent_patterns: List[Tuple[Intent, List[str]]] = [
            (Intent.CROP_QUERY, ["crop", "crops", "फसल", "पिके", "planted"]),
            (Intent.MARKET_QUERY, ["price", "prices", "market", "भाव", "दर", "rate", "mandi", "मंडी"]),
            (Intent.SCHEME_QUERY, ["scheme", "schemes", "yojana", "योजना", "subsidy", "subsidies"]),
            (Intent.PEST_QUERY, ["pest", "aphid", "aphids", "insects", "कीट", "कीड", "whitefly"]),
            (Intent.DISEASE_QUERY, ["disease", "wilt", "blight", "sick", "रोग", "आजारी"]),
            (Intent.WEATHER_QUERY, ["weather", "rain", "temperature", "forecast", "मौसम", "हवामान", "पाऊस"]),
            (Intent.LAND_QUERY, ["land", "records", "farm area", "acres", "जमीन", "जमिनीचा"]),
            (Intent.INVENTORY_QUERY, ["inventory", "stock", "instock", "godown", "साठा"]),
            (Intent.PROFILE_QUERY, ["profile", "my details", "account", "प्रोफाइल"]),
            (Intent.FERTILIZER_QUERY, ["fertilizer", "urea", "dap", "खत", "उर्वरक"]),
            (Intent.SOIL_HEALTH_QUERY, ["soil", "health", "ph level", "माती", "मिट्टी"]),
            (Intent.FARMING_TIPS_QUERY, ["tip", "tips", "advice", "सल्ला", "सुझाव", "calendar"]),
        ]

    def classify(self, text: str) -> IntentResult:
        """Analyzes text and returns the most confident IntentResult."""
        text_lower = text.lower()
        
        best_intent = Intent.UNKNOWN
        max_matches = 0
        
        for intent, keywords in self.intent_patterns:
            matches = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
            # Also check substring for non-latin scripts (Hindi/Marathi)
            matches += sum(1 for kw in keywords if kw in text_lower and not kw.isascii())
            
            if matches > max_matches:
                max_matches = matches
                best_intent = intent
                
        if max_matches >= 2:
            confidence = 0.95
            reason = f"Strong match found with {max_matches} keywords."
        elif max_matches == 1:
            confidence = 0.75
            reason = "Partial match found with 1 keyword."
        else:
            confidence = 0.10
            reason = "No known patterns matched."
            
        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            reason=reason
        )
