# TravelBuddy

Python console chatbot for planning a weekend getaway.

## Setup

1. Open this folder as a project in PyCharm.
2. Install Python 3.11 or newer and create a project virtual environment (`.venv`).
3. In the project terminal, run `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and add your OpenRouter API key.
5. Run `python main.py`, or run `main.py` from PyCharm.

Configuration loading, validation, and client initialization are implemented. The trip-planning conversation is still starter scaffolding.
The OpenAI Python SDK can be configured to call OpenRouter's compatible API.

## Project structure

```text
TravelBuddy/
|-- main.py              # Entry point and console input/output
|-- chatbot.py           # Conversation flow, state, and trip choices
|-- llm_client.py        # OpenRouter API integration
|-- config.py            # Environment variables and settings
|-- requirements.txt
|-- .env.example
|-- .gitignore
`-- README.md
```

The entry point validates settings, initializes and closes the OpenRouter client, and prints a starter message from `chatbot.py`. It does not send a model request yet.

## Implementation checklist

- Greet the user in an upbeat, friendly tone.
- Guide trip type, accommodation, and activities, with three options at each step.
- Make activities appropriate for the trip type.
- Preserve conversation history and previous choices.
- Handle unexpected input and guide the user back to the current step.
- Summarize the final plan; say goodbye and quit on `exit`.
- Use the specified OpenRouter model, or a free OpenRouter model if unavailable.

## Example conversation

TODO: Add an actual example after implementation.

## Design decisions

TODO: Explain conversation state, prompting, and error handling.

## Git

This folder has its own Git repository. Make meaningful commits while developing.
The GitHub repository is https://github.com/NinoKk27/TravelBuddy. Keep `.env` out of Git.

## Configuration and current scope

The requirements checklist above is the working specification from this README;
it has not yet been checked against the original programming assignment.

- `config.py` reads `.env` beside the source files, regardless of the working directory.
- Existing environment variables override `.env` values. Both `OPENROUTER_API_KEY`
  and `OPENROUTER_MODEL` are required; blank values and the example key are rejected.
- Settings are immutable, and their representation hides the API key.
- `llm_client.py` constructs the OpenRouter client with a 30-second timeout and
  up to two retries. Client construction does not authenticate or send a request.
- `main.py` handles configuration errors with a readable message and exit code 1.
- `chatbot.py` remains responsible for the future conversation flow.

Copy `.env.example` to `.env`, replace the placeholder key, and set the model
required by the assignment. The example model's availability has not been verified.
Never commit `.env`. Model requests and chat behavior are later implementation steps.

OpenRouter's SDK compatibility reference: https://openrouter.ai/blog/tutorials/any-coding-agent/
