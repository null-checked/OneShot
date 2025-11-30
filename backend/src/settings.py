from pydantic_settings import BaseSettings

from src.core.pipeline import MultiAgentPipeline
from src.core.architect_pipeline import ArchitectPipeline
from src.core.filesystem_writer import FilesystemWriter

class Settings(BaseSettings):
    """
    Manages config via Environment Variables.
    Example: export APP_PORT=8001 overrides the default.
    """
    APP_NAME: str = "Telekom Hackathon MultiAgent Backend"
    APP_HOST: str = "localhost"
    APP_PORT: int = 8000
    RELOAD: bool = True
    # In production, this should be a strict list of domains
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    OPENAI_API_KEY: str

    # Pipeline configuration
    USE_ARCHITECT_PIPELINE: bool = True  # Set to True to use new architect-based pipeline
    MAX_AGENT_RETRIES: int = 5

    class Config:
        env_file = ".env"


settings = Settings()

def get_pipeline_agent():
    """
    Get the pipeline agent based on configuration.
    Returns ArchitectPipeline if USE_ARCHITECT_PIPELINE is True, otherwise MultiAgentPipeline.
    """
    if settings.USE_ARCHITECT_PIPELINE:
        return ArchitectPipeline(
            openai_api_key=settings.OPENAI_API_KEY,
            max_retries=settings.MAX_AGENT_RETRIES
        )
    else:
        return MultiAgentPipeline(settings.OPENAI_API_KEY)

fs_writer = FilesystemWriter()
