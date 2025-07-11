from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Gmail API settings
    GMAIL_CREDENTIALS_PATH: str = "credentials.json"
    GMAIL_TOKEN_PATH: str = "token.json"
    GMAIL_SCOPES: list = ["https://www.googleapis.com/auth/gmail.modify"]
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./auto_responder.db"
    
    # Redis settings for caching
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Email processing settings
    MAX_BATCH_SIZE: int = 10
    PROCESSING_DELAY: int = 2  # seconds
    
    model_config = {
        "env_file": ".env"
    }

settings = Settings()