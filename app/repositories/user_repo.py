from sqlalchemy import text
from app.repositories.base import BaseRepository
from app.core.security import sanitize_user_data

class UserRepository(BaseRepository):
    """Handles data access for user_master and role mappings."""
    
    def get_user_by_id(self, user_id: int) -> dict | None:
        """
        Retrieves user data by ID, strictly excluding passwords.
        Applies PII sanitization before returning.
        """
        query = text("""
            SELECT u.user_id, u.full_name as name, u.mobile_number, u.role_id,
                   s.state_name as state, d.district_name as district
            FROM user_master u
            LEFT JOIN state s ON u.state_id = s.state_id
            LEFT JOIN district d ON u.district_id = d.district_id
            WHERE u.user_id = :user_id AND u.is_active = 1
        """)
        
        result = self._execute(query, {"user_id": user_id}).mappings().first()
        if not result:
            return None
            
        return sanitize_user_data(dict(result))
