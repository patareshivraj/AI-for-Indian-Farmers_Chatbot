from typing import Optional, Dict, Any
from app.memory.models import TrackedEntities
from app.memory.persistence import MemoryPersistence

class EntityTracker:
    """Tracks named entities (crops, districts) over a 24-hour conversation window."""
    
    TTL_MINUTES = 24 * 60  # 24 Hours
    MEMORY_TYPE = "entities"

    def __init__(self, persistence: MemoryPersistence):
        self.persistence = persistence

    def get_entities(self, session_id: str, user_id: int) -> TrackedEntities:
        payload = self.persistence.load(session_id, user_id, self.MEMORY_TYPE)
        if not payload:
            return TrackedEntities()
        return TrackedEntities(**payload)

    def update_entities(self, session_id: str, user_id: int, new_parameters: Dict[str, Any]) -> None:
        """Updates the tracked entities with newly discovered parameters."""
        entities = self.get_entities(session_id, user_id)
        
        # We only want to track certain fields
        tracking_keys = TrackedEntities.model_fields.keys()
        
        updated = False
        for key, value in new_parameters.items():
            if key in tracking_keys and value is not None:
                setattr(entities, key, str(value))
                updated = True
                
        if updated:
            self.persistence.save(
                session_id=session_id,
                user_id=user_id,
                memory_type=self.MEMORY_TYPE,
                payload=entities.model_dump(mode="json")
            )

    def clean_expired(self) -> None:
        """Purges entity tracking older than 24 hours."""
        self.persistence.delete_expired(self.MEMORY_TYPE, self.TTL_MINUTES)
