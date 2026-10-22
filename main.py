"""TravelBuddy console entry point and optional live connection check."""

import argparse
import sys

from openai import OpenAIError

from chatbot import Step, TravelBuddy
from config import ConfigurationError, load_settings
from llm_client import create_client, request_reply


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Plan a weekend with TravelBuddy.")
    parser.add_argument("--check-api", action="store_true", help="Send one short live model request and quit.")
    args = parser.parse_args(argv)
    try:
        settings = load_settings()
    except ConfigurationError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    if args.check_api:
        try:
            with create_client(settings) as client:
                reply = request_reply(client, settings.model, [
                    {"role": "user", "content": "Reply with a short greeting for a travel planner."}
                ])
            print(f"Model response: {reply}")
            return 0
        except (OpenAIError, ValueError) as error:
            # Do not print provider error bodies, which may contain sensitive details.
            print(f"API check failed ({type(error).__name__}). Check your key, model, and connection.", file=sys.stderr)
            return 1

    bot = TravelBuddy()
    print(bot.start())
    while bot.state.step not in (Step.SUMMARY, Step.EXITED):
        try:
            message = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\n" + bot.respond("exit"))
            break
        print(bot.respond(message))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
