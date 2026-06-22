import re
from typing import Dict, Any

class ParameterExtractor:
    """Extracts typed parameters from natural language."""

    def __init__(self):
        # Canonical mappings for deterministic V1 extraction
        self.crops = {
            "soybean": ["soybean", "सोयाबीन"],
            "cotton": ["cotton", "कापूस", "कपास"],
            "wheat": ["wheat", "गहू", "गेहूं"],
            "rice": ["rice", "तांदूळ", "चावल"],
            "sugarcane": ["sugarcane", "ऊस", "गन्ना"]
        }
        self.districts = {
            "Pune": ["pune", "पुणे"],
            "Nashik": ["nashik", "नाशिक", "नासिक"],
            "Nagpur": ["nagpur", "नागपूर", "नागपुर"],
            "Satara": ["satara", "सातारा"],
            "Aurangabad": ["aurangabad", "औरंगाबाद"]
        }
        self.states = {
            "Maharashtra": ["maharashtra", "महाराष्ट्र"],
            "Gujarat": ["gujarat", "गुजरात"],
            "Karnataka": ["karnataka", "कर्नाटक"],
            "Madhya Pradesh": ["mp", "madhya pradesh", "मध्य प्रदेश"]
        }
        self.pests = {
            "aphids": ["aphid", "aphids", "मावा"],
            "whitefly": ["whitefly", "पांढरी माशी"],
            "bollworm": ["bollworm", "बोंडअळी"],
            "locust": ["locust", "टोळ"]
        }
        self.diseases = {
            "wilt": ["wilt", "मर"],
            "blight": ["blight", "करपा"],
            "rust": ["rust", "तांबेरा"],
            "smut": ["smut", "काणी"]
        }
        self.genders = {
            "female": ["women", "female", "mahila", "महिला"]
        }
        self.categories = {
            "sc": ["sc"], "st": ["st"], "obc": ["obc"], "general": ["general"],
            "equipment": ["equipment", "औजार"], "irrigation": ["irrigation", "सिंचन"]
        }

    def extract(self, text: str) -> Dict[str, Any]:
        """Extracts all known entities from the text into a flat dictionary."""
        text_lower = text.lower()
        params = {}

        def _extract_entity(entity_dict):
            for canonical, synonyms in entity_dict.items():
                for syn in synonyms:
                    if syn in text_lower:
                        return canonical
            return None

        crop = _extract_entity(self.crops)
        if crop: params["crop_name"] = crop

        district = _extract_entity(self.districts)
        if district: params["district"] = district

        state = _extract_entity(self.states)
        if state: params["state"] = state

        pest = _extract_entity(self.pests)
        if pest: params["pest_name"] = pest

        disease = _extract_entity(self.diseases)
        if disease: params["disease_name"] = disease

        gender = _extract_entity(self.genders)
        if gender: params["gender"] = gender

        category = _extract_entity(self.categories)
        if category: params["category"] = category

        return params
