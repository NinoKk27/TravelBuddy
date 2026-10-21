# TravelBuddy

Python console chatbot for planning a weekend getaway.

## Setup

1. Open this folder as a project in PyCharm.
2. Install Python 3.11 or newer and create a project virtual environment (`.venv`).
3. In the project terminal, run `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and add your OpenRouter API key.
5. Run `python main.py`, or run `main.py` from PyCharm.

`main.py` is a placeholder; the assignment solution has not been implemented yet.
The OpenAI Python SDK can be configured to call OpenRouter's compatible API.

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
Connect it to a GitHub repository before submission. Keep `.env` out of Git.
