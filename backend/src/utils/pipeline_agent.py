from src.settings import settings
from src.core.architect_pipeline import ArchitectPipeline
from src.core.pipeline import MultiAgentPipeline


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