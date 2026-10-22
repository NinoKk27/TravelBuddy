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


def api_error_message(error: Exception) -> str:
    """Translate API failures without exposing raw provider bodies or credentials."""
    from openai import (
        APIConnectionError, APIStatusError, APITimeoutError,
        AuthenticationError, PermissionDeniedError, RateLimitError,
    )

    if isinstance(error, AuthenticationError):
        return "The AI service rejected the API key. Check OPENROUTER_API_KEY in .env."
    if isinstance(error, PermissionDeniedError):
        return "The AI service denied access. Check your account and model permissions."
    if isinstance(error, RateLimitError):
        return "The AI service is busy or rate-limited. Please try again later."
    if isinstance(error, APITimeoutError):
        return "The AI service took too long to respond. Please try again later."
    if isinstance(error, APIConnectionError):
        return "Could not connect to the AI service. Check your internet connection."
    if isinstance(error, APIStatusError):
        if error.status_code == 402:
            return "The AI service requires credits. Check your OpenRouter balance."
        if error.status_code in (400, 404, 422):
            return "The AI service could not process the request. Check OPENROUTER_MODEL and its availability."
        return "The AI service is temporarily unavailable. Please try again later."
    if isinstance(error, ValueError):
        return "The AI service returned no usable text. Please try again later."
    return "The AI request failed. Please try again later."


class ModelAssistant:
    """Injectable model adapter; failures leave the guided planner usable."""

    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def __call__(self, messages: list[dict[str, str]]) -> str:
        from openai import OpenAIError

        try:
            return request_reply(self.client, self.model, messages)
        except (OpenAIError, ValueError) as error:
            return api_error_message(error) + " You can still use the planner below."
