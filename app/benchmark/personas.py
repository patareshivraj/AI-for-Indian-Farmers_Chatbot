import json
import random
import os
from typing import List, Dict, Any
from app.context.models import RoleEnum, LanguageEnum

class PersonaGenerator:
    """Generates synthetic users for benchmarking."""
    
    STATES = ["Maharashtra", "Gujarat", "Karnataka", "Punjab", "Madhya Pradesh"]
    DISTRICTS = {
        "Maharashtra": ["Pune", "Nashik", "Nagpur"],
        "Gujarat": ["Ahmedabad", "Surat", "Rajkot"],
        "Karnataka": ["Bangalore", "Mysore", "Hubli"],
        "Punjab": ["Amritsar", "Ludhiana", "Jalandhar"],
        "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior"]
    }
    CROPS = ["soybean", "cotton", "wheat", "rice", "sugarcane", "maize"]

    @classmethod
    def generate_personas(cls, role: RoleEnum, count: int, seed: int = 42) -> List[Dict[str, Any]]:
        random.seed(seed)
        personas = []
        
        for i in range(count):
            role_multiplier = 1 if role == RoleEnum.FARMER else 2 if role == RoleEnum.CONSULTANT else 3
            user_id = (role_multiplier * 10000) + i + 1
            state = random.choice(cls.STATES)
            district = random.choice(cls.DISTRICTS[state])
            lang = random.choice(list(LanguageEnum))
            
            persona = {
                "user_id": user_id,
                "role": role.value,
                "name": f"Test {role.value} {i}",
                "state": state,
                "district": district,
                "language": lang.value
            }
            
            if role == RoleEnum.FARMER:
                persona["farm_size"] = round(random.uniform(1.0, 50.0), 2)
                persona["crop_types"] = random.sample(cls.CROPS, k=random.randint(1, 3))
            elif role == RoleEnum.CONSULTANT:
                persona["consultant_specialization"] = random.choice(["Agronomy", "Pest Control", "Soil Health"])
                
            personas.append(persona)
            
        return personas

    @classmethod
    def write_datasets(cls, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        
        farmers = cls.generate_personas(RoleEnum.FARMER, 1000)
        with open(os.path.join(output_dir, "farmers.json"), "w") as f:
            json.dump(farmers, f, indent=2)
            
        consultants = cls.generate_personas(RoleEnum.CONSULTANT, 50)
        with open(os.path.join(output_dir, "consultants.json"), "w") as f:
            json.dump(consultants, f, indent=2)
            
        admins = cls.generate_personas(RoleEnum.ADMIN, 5)
        with open(os.path.join(output_dir, "admins.json"), "w") as f:
            json.dump(admins, f, indent=2)

if __name__ == "__main__":
    dataset_dir = os.path.join(os.path.dirname(__file__), "datasets")
    PersonaGenerator.write_datasets(dataset_dir)
