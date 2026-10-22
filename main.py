"""TravelBuddy console application entry point."""

import sys

from chatbot import get_startup_message
from config import ConfigurationError, load_settings
from llm_client import create_client


def main() -> int:
    """Validate settings and initialize the client before starting the app."""
    try:
        settings = load_settings()
    except ConfigurationError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    with create_client(settings):
        print(get_startup_message())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
