from sqlalchemy import text
from app.repositories.base import BaseRepository
from app.core.security import sanitize_land_record

class FarmerRepository(BaseRepository):
    """Handles data access for farmer specific metrics and crops."""
    
    def get_farmer_profile(self, user_id: int) -> dict:
        """Retrieves profile preferences like language and experience."""
        query = text("""
            SELECT preferred_language, farming_experience, total_land_area
            FROM farmer_profile
            WHERE user_id = :user_id
        """)
        result = self._execute(query, {"user_id": user_id}).mappings().first()
        return dict(result) if result else {}
        
    def get_farm_metrics(self, user_id: int) -> dict:
        """Aggregates active land records, crop details, and total area."""
        
        # 1. Total Land Area from Profile
        profile_query = text("SELECT total_land_area FROM farmer_profile WHERE user_id = :user_id")
        profile = self._execute(profile_query, {"user_id": user_id}).mappings().first()
        total_land_area = float(profile["total_land_area"]) if profile and profile["total_land_area"] else 0.0
        
        # 2. Active Land IDs
        land_query = text("SELECT id FROM farmer_land_records WHERE farmer_id = :user_id")
        lands = self._execute(land_query, {"user_id": user_id}).fetchall()
        land_ids = [row[0] for row in lands]
        
        # 3. Active Crops
        crops = []
        if land_ids:
            # farmer_crop_details requires land_id and farmer_id string matching as per schema
            crop_query = text("""
                SELECT DISTINCT crop_name 
                FROM farmer_crop_details 
                WHERE farmer_id = :user_id AND is_crop_planted = 1
            """)
            crop_results = self._execute(crop_query, {"user_id": str(user_id)}).fetchall()
            crops = [row[0] for row in crop_results]
            
        return {
            "total_land_area_acres": total_land_area,
            "active_land_count": len(land_ids),
            "active_crops": crops,
            "land_ids": land_ids
        }
