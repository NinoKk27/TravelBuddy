"""OpenRouter client construction, separate from conversation and console I/O."""

from openai import OpenAI

from config import Settings

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def create_client(settings: Settings) -> OpenAI:
    """Construct a client from validated settings; this sends no API request.

    The model is supplied as settings.model when making a completion request.
    """
    return OpenAI(
        api_key=settings.api_key,
        base_url=OPENROUTER_BASE_URL,
        timeout=30.0,
        max_retries=2,
    )
