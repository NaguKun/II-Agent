from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    mongodb_url: str = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
    database_name: str = "chat_app"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    max_file_size_mb: int = 10
    allowed_image_types: str = "image/jpeg,image/png,image/jpg"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
