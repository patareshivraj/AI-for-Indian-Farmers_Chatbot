from sqlalchemy import text
from app.repositories.base import BaseRepository

class ConsultantRepository(BaseRepository):
    """Handles data access for consultant assignments."""
    
    def get_authorized_farmers(self, consultant_id: int) -> list[int]:
        """Retrieves list of farmer IDs that accepted this consultant's request."""
        query = text("""
            SELECT farmer_id 
            FROM farmer_consultant_requests 
            WHERE consultant_id = :consultant_id AND status = 'ACCEPTED'
        """)
        
        results = self._execute(query, {"consultant_id": consultant_id}).fetchall()
        return [row[0] for row in results]
