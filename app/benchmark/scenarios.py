import json
import os

def create_static_datasets(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    
    multilingual = [
        {"query": "सोयाबीनसाठी कोणती योजना आहे?", "expected_intent": "SCHEME_QUERY", "language": "mr"},
        {"query": "कापसावर whitefly नियंत्रण कसे करावे?", "expected_intent": "PEST_QUERY", "language": "mr"},
        {"query": "मुझे सोयाबीन के बाजार भाव बताओ", "expected_intent": "MARKET_QUERY", "language": "hi"},
        {"query": "What is the weather in Pune?", "expected_intent": "WEATHER_QUERY", "language": "en"}
    ]
    with open(os.path.join(output_dir, "multilingual.json"), "w", encoding="utf-8") as f:
        json.dump(multilingual, f, indent=2, ensure_ascii=False)
        
    reasoning = [
        {"query": "Should I plant soybean next month?", "expected_intent": "CROP_PLANNING_QUERY"},
        {"query": "Am I eligible for any scheme?", "expected_intent": "SCHEME_ELIGIBILITY_QUERY"},
        {"query": "How is my farm performing?", "expected_intent": "FARM_HEALTH_QUERY"}
    ]
    with open(os.path.join(output_dir, "reasoning.json"), "w", encoding="utf-8") as f:
        json.dump(reasoning, f, indent=2)
        
    memory = [
        {
            "sequence": [
                {"query": "Show soybean prices in Pune", "expected_intent": "MARKET_QUERY"},
                {"query": "What about Nashik?", "expected_intent": "MARKET_QUERY"}, # Inherits crop=soybean
                {"query": "And cotton?", "expected_intent": "MARKET_QUERY"} # Inherits district=Nashik
            ]
        }
    ]
    with open(os.path.join(output_dir, "memory.json"), "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

if __name__ == "__main__":
    dataset_dir = os.path.join(os.path.dirname(__file__), "datasets")
    create_static_datasets(dataset_dir)
