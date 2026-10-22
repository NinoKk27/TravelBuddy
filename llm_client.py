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


def request_reply(client: OpenAI, model: str, messages: list[dict[str, str]], *, max_tokens: int = 150) -> str:
    """Send messages to the configured model and return a nonempty text reply."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )
    if not response.choices:
        raise ValueError("The model returned no response choices.")
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("The model returned no text.")
    return content.strip()
