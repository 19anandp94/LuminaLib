from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://luminalib:luminalib@localhost:5432/luminalib"
    jwt_secret_key: str = "change-in-production"
    token_expire_minutes: int = 60
    storage_provider: str = "local"
    local_storage_path: str = "./uploads"
    aws_bucket: str = ""
    aws_region: str = "us-east-1"
    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    recommendation_engine: str = "hybrid"

    class Config:
        env_file = ".env"


settings = Settings()

