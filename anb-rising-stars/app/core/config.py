"""
Application configuration settings.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "ANB Rising Stars Showcase"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/anb_rising_stars"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 300

    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # File Storage - Use absolute paths
    upload_dir: str = "/app/uploads"
    processed_dir: str = "/app/processed"
    max_file_size: int = 104857600  # 100MB
    allowed_video_formats: List[str] = ["mp4"]

    # Video Processing
    video_min_duration: int = 20  # seconds
    video_max_duration: int = 60  # seconds
    video_processed_max_duration: int = 19  # seconds
    video_output_resolution: str = "720p"
    video_aspect_ratio: str = "16:9"
    video_intro_outro_duration: int = 5  # seconds

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
