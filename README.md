# TravelBuddy

Python console chatbot for planning a weekend getaway.

## Setup

1. Open this folder as a project in PyCharm.
2. Install Python 3.11 or newer and create a project virtual environment (`.venv`).
3. In the project terminal, run `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and add your OpenRouter API key.
5. Run `python main.py`, or run `main.py` from PyCharm.

Configuration loading, validation, and client initialization are implemented. The greeting and trip-type selection are implemented; accommodation and activities are pending.
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

The entry point validates settings and runs the greeting and trip-type selection. Use `python main.py --check-api` to send a separate short model request.

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
- `main.py` handles configuration errors with a readable message and exit code 1, and runs the console interaction.
- `chatbot.py` owns conversation state, per-session message history, the greeting, and trip selection.

Copy `.env.example` to `.env`, replace the placeholder key, and set the model
required by the assignment. The example model's availability has not been verified.
Never commit `.env`. Connecting model responses to the guided conversation is a later step.

OpenRouter's SDK compatibility reference: https://openrouter.ai/blog/tutorials/any-coding-agent/

## Steps 6-10: first conversation stage

Run `python main.py`. Choose `1` (Beach getaway), `2` (Mountain adventure),
or `3` (City break); full option names also work, ignoring case and surrounding
spaces. These are starter options pending confirmation of the original assignment.
The bot records the choice and advances its state to accommodation. This milestone
then ends the console session; accommodation selection will be implemented next.
Choices and history are in memory only and reset when the application restarts.

The state also reserves fields for accommodation and activity. History stores the
assistant greeting, user messages, and assistant replies in order. Basic invalid-input
handling and `exit` support keep this first stage usable. Model-generated responses
are not yet connected to the guided conversation.

Run `python main.py --check-api` to send one short request using the configured model.
The request helper follows https://github.com/OpenRouterTeam/openrouter-examples-python/blob/main/src/openai_test.py.
Live verification is pending: no API key was configured when this stage was implemented.
Configure `.env` locally before running the check; do not put the key in chat or Git.

Run the offline tests from the project folder:

```text
python -m unittest discover -s tests -v
```
