from typing import Optional
from app.memory.models import ConversationState
from app.memory.persistence import MemoryPersistence

class SessionStore:
    """Manages the short-lived active conversation session state."""
    
    TTL_MINUTES = 30
    MEMORY_TYPE = "session_state"

    def __init__(self, persistence: MemoryPersistence):
        self.persistence = persistence

    def get_session(self, session_id: str, user_id: int) -> Optional[ConversationState]:
        payload = self.persistence.load(session_id, user_id, self.MEMORY_TYPE)
        if not payload:
            return None
        return ConversationState(**payload)

    def update_session(self, state: ConversationState) -> None:
        self.persistence.save(
            session_id=state.session_id,
            user_id=state.user_id,
            memory_type=self.MEMORY_TYPE,
            payload=state.model_dump(mode="json")
        )

    def clean_expired(self) -> None:
        """Purges sessions older than 30 minutes."""
        self.persistence.delete_expired(self.MEMORY_TYPE, self.TTL_MINUTES)
