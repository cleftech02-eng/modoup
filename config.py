from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Modo Up"
    ENVIRONMENT: str = "development"         
    DEBUG: bool = True
    DATABASE_URL: str                         
    SECRET_KEY: str                        
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7   

    
    model_config = SettingsConfigDict(
        env_file=".venv",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()