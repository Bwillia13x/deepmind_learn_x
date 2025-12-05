"""Application configuration."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # App info
    app_name: str = "Alberta ESL AI API"
    environment: str = "dev"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    database_url: str = "postgresql+psycopg://dev:devpass@localhost:5432/ab_esl_ai"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # MinIO/S3
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "ab-esl"

    # Feature flags
    enable_asr: bool = True
    enable_llm: bool = True
    save_audio_by_default: bool = False
    save_transcripts_by_default: bool = False
    l1_enabled_by_default: bool = True

    # ASR settings
    asr_model: str = "small"
    asr_compute_type: str = "int8"
    asr_device: str = "cpu"

    # LLM settings (optional external API)
    llm_api_url: str = ""
    llm_api_key: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"
        env_file_encoding = "utf-8"


settings = Settings()
