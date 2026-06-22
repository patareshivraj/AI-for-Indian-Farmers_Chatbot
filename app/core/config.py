from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://user:password@localhost:3306/farm360"
    context_cache_ttl_seconds: int = 300

    class Config:
        env_file = ".env"

settings = Settings()
