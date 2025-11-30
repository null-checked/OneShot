from src.core.pipeline import MultiAgentPipeline
from src.settings import settings

def get_pipeline_agent():
    return MultiAgentPipeline(settings.OPENAI_API_KEY)
