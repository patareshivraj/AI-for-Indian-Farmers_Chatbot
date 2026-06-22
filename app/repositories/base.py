from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.exceptions import RepositoryError

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class BaseRepository:
    """Base class for all database repositories."""
    
    def __init__(self, session=None):
        self.session = session or SessionLocal()
        
    def _execute(self, query, params=None):
        try:
            return self.session.execute(query, params)
        except Exception as e:
            self.session.rollback()
            raise RepositoryError(f"Database query failed: {str(e)}")
            
    def close(self):
        if self.session:
            self.session.close()
