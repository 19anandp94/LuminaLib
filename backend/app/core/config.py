"""
Application configuration management.
Uses pydantic-settings for type-safe configuration from environment variables.
"""
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql://lumina:lumina_password@localhost:5432/luminalib",
        description="PostgreSQL connection string",
    )

    # JWT
    jwt_secret_key: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key for JWT token generation",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="JWT token expiration in minutes"
    )

    # Storage
    storage_provider: str = Field(
        default="local", description="Storage provider: local, minio, s3"
    )
    storage_local_path: str = Field(
        default="/app/book_storage", description="Local storage path"
    )
    minio_endpoint: str = Field(default="localhost:9000", description="MinIO endpoint")
    minio_access_key: str = Field(default="minioadmin", description="MinIO access key")
    minio_secret_key: str = Field(default="minioadmin", description="MinIO secret key")
    minio_bucket: str = Field(default="books", description="MinIO bucket name")
    aws_access_key_id: str = Field(default="", description="AWS access key")
    aws_secret_access_key: str = Field(default="", description="AWS secret key")
    aws_bucket_name: str = Field(default="", description="AWS S3 bucket name")
    aws_region: str = Field(default="us-east-1", description="AWS region")

    # LLM
    llm_provider: str = Field(
        default="ollama", description="LLM provider: ollama, openai, mock"
    )
    llm_model: str = Field(default="llama3", description="LLM model name")
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama base URL"
    )
    openai_api_key: str = Field(default="", description="OpenAI API key")

    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        description="CORS allowed origins",
    )

    # Redis (for Celery)
    redis_url: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    @property
    def async_database_url(self) -> str:
        """Get async database URL for SQLAlchemy."""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")


# Global settings instance
settings = Settings()

