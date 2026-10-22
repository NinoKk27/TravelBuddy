"""Load and validate application settings without exposing credentials."""

from dataclasses import dataclass, field
import os
from pathlib import Path

from dotenv import dotenv_values

ENV_FILE = Path(__file__).resolve().parent / ".env"


class ConfigurationError(ValueError):
    """Raised when required application settings are missing or invalid."""


@dataclass(frozen=True)
class Settings:
    api_key: str = field(repr=False)
    model: str

    def __post_init__(self):
        for name, value in (("OPENROUTER_API_KEY", self.api_key),
                            ("OPENROUTER_MODEL", self.model)):
            if not value or not value.strip():
                raise ConfigurationError(
                    f"Set {name} in TravelBuddy's .env file or your environment."
                )
            if value.strip() == "replace_with_your_key":
                raise ConfigurationError(
                    "Replace OPENROUTER_API_KEY in .env with your OpenRouter API key."
                )
        object.__setattr__(self, "api_key", self.api_key.strip())
        object.__setattr__(self, "model", self.model.strip())


def load_settings(env_file: Path = ENV_FILE) -> Settings:
    """Read the project .env; existing environment variables take precedence."""
    values = dotenv_values(env_file, interpolate=False)
    return Settings(
        api_key=os.environ.get("OPENROUTER_API_KEY", values.get("OPENROUTER_API_KEY")) or "",
        model=os.environ.get("OPENROUTER_MODEL", values.get("OPENROUTER_MODEL")) or "",
    )
