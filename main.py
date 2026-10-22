"""TravelBuddy console entry point and optional live connection check."""

import argparse
import sys

from openai import OpenAIError

from chatbot import Step, TravelBuddy
from config import ConfigurationError, load_settings
from llm_client import ModelAssistant, api_error_message, create_client, request_reply


def run_conversation(bot: TravelBuddy) -> int:
    print(bot.start())
    while bot.state.step != Step.EXITED:
        try:
            message = input("You: ")
            reply = bot.respond(message)
        except (EOFError, KeyboardInterrupt):
            print("\n" + bot.respond("exit"))
            break
        print(reply)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Plan a weekend with TravelBuddy.")
    parser.add_argument("--check-api", action="store_true", help="Send one short live model request and quit.")
    args = parser.parse_args(argv)
    try:
        settings = load_settings()
    except ConfigurationError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    try:
        with create_client(settings) as client:
            if args.check_api:
                reply = request_reply(client, settings.model, [
                    {"role": "user", "content": "Reply with a short greeting for a travel planner."}
                ])
                print(f"Model response: {reply}")
                return 0
            return run_conversation(TravelBuddy(ModelAssistant(client, settings.model)))
    except (OpenAIError, ValueError) as error:
        print(api_error_message(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nGoodbye! Have a wonderful next adventure!")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
