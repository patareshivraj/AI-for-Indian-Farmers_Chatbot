import json
import os

dataset = []

# Generate Crop Queries
for crop in ["soybean", "cotton", "wheat", "rice", "sugarcane", "bajra", "jowar"]:
    for action in ["Show", "What are", "List", "Get me", "Tell me about"]:
        for qualifier in ["my", "the", "all my", "active"]:
            dataset.append({
                "question": f"{action} {qualifier} crops like {crop}",
                "expected_intent": "CROP_QUERY",
                "role": "Farmer"
            })

# Generate Market Queries
for district in ["Pune", "Nashik", "Nagpur", "Satara", "Aurangabad"]:
    for crop in ["soybean", "cotton", "wheat", "rice", "onion"]:
        for term in ["price", "rate", "market", "mandi rate"]:
            dataset.append({
                "question": f"What is the {term} for {crop} in {district}?",
                "expected_intent": "MARKET_QUERY",
                "role": "Consultant"
            })

# Generate Scheme Queries
for state in ["Maharashtra", "Gujarat", "Karnataka", "MP"]:
    for category in ["women", "general", "SC/ST", "irrigation", "equipment"]:
        dataset.append({
            "question": f"Are there any {category} schemes available in {state}?",
            "expected_intent": "SCHEME_QUERY",
            "role": "Farmer"
        })

# Generate Pest Queries
for pest in ["aphids", "whitefly", "bollworm", "locust"]:
    for crop in ["cotton", "soybean"]:
        dataset.append({
            "question": f"How to control {pest} insects on {crop}?",
            "expected_intent": "PEST_QUERY",
            "role": "Farmer"
        })

# Unknown Queries
unknowns = [
    "Explain quantum physics", "Who is the prime minister?",
    "How to build an app", "What is the capital of France?",
    "Give me a recipe for cake"
]
for q in unknowns:
    dataset.append({
        "question": q,
        "expected_intent": "UNKNOWN",
        "role": "Admin"
    })

# Write to file
output_path = os.path.join(os.path.dirname(__file__), "router_dataset.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4, ensure_ascii=False)

print(f"Generated {len(dataset)} examples in {output_path}")
