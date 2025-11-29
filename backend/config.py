from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    LLM_PROVIDER: Literal["ollama", "openai", "custom"] = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    CUSTOM_BASE_URL: Optional[str] = None
    CUSTOM_MODEL: Optional[str] = None
    CUSTOM_API_KEY: Optional[str] = None
    HOST: str = "0.0.0.0"
    PORT: int = 8000


settings = Settings()
