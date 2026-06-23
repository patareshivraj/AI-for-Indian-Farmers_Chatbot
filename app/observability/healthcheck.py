from typing import Dict, Any

class HealthChecker:
    """Manages system health and readiness checks."""
    
    @classmethod
    def check_health(cls) -> Dict[str, Any]:
        """Simple liveness check. Used for /health"""
        return {
            "status": "UP"
        }
        
    @classmethod
    def check_readiness(cls) -> Dict[str, Any]:
        """Deep check of dependencies. Used for /ready"""
        # In a real app, this would ping the database, cache, and LLM
        components = {
            "database": "UP",
            "memory_store": "UP",
            "llm_provider": "UP",
            "reasoning_engine": "UP",
            "tool_registry": "UP"
        }
        
        status = "UP" if all(v == "UP" for v in components.values()) else "DOWN"
        
        return {
            "status": status,
            "components": components
        }
