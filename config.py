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

    # Sliding window configuration
    sliding_window_enabled: bool = True
    sliding_window_max_messages: int = 20  # Maximum messages to keep in context
    sliding_window_preserve_first: int = 2  # Always keep first N messages for context
    sliding_window_token_limit: int = 100000  # Soft token limit (for GPT-4)

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
