# TravelBuddy

Python console chatbot for planning a weekend getaway.

## Setup

1. Open this folder as a project in PyCharm.
2. Install Python 3.11 or newer and create a project virtual environment (`.venv`).
3. In the project terminal, run `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and add your OpenRouter API key.
5. Run `python main.py`, or run `main.py` from PyCharm.

Configuration loading, validation, and client initialization are implemented. The greeting, trip-type selection, accommodation selection, and trip-specific activity selection are implemented with input validation.
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

The entry point validates settings and runs all three guided selection stages. Use `python main.py --check-api` to send a separate short model request.

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
Never commit `.env`. Normal conversations now call the configured model after each non-exit answer.

OpenRouter's SDK compatibility reference: https://openrouter.ai/blog/tutorials/any-coding-agent/

## Guided selection: steps 7-15

Run `python main.py` and choose an option number or full name at each stage.
Matching ignores case and extra whitespace. Each stage offers three options:

- Trip type: Beach getaway, Mountain adventure, or City break.
- Accommodation: Hotel, Hostel, or Vacation rental.
- Beach activities: Swimming, Snorkeling, or Sunset beach walk.
- Mountain activities: Hiking, Mountain biking, or Stargazing.
- City activities: Museum visit, Food tour, or Walking tour.

These are starter options pending confirmation of the original assignment.
Invalid input repeats the current menu without changing the step or earlier choices.
Activities from another trip type are rejected. Type `exit` at any selection stage
for a goodbye; closing input or pressing Ctrl+C also ends the conversation cleanly.

After activity selection, all three choices are stored and the state advances to
`SUMMARY`. The bot displays the exact saved trip type, accommodation, and activity,
then accepts follow-up questions until the user types `exit`. Choices and message history
are in memory only and reset when the application restarts. History preserves the
assistant greeting and each user/assistant exchange, including invalid answers.

Run `python main.py --check-api` to send one short request using the configured model.
The request helper follows https://github.com/OpenRouterTeam/openrouter-examples-python/blob/main/src/openai_test.py.
Live verification is pending: no API key was configured when this stage was implemented.
Configure `.env` locally before running the check; do not put the key in chat or Git.

Run the offline tests from the project folder:

```text
python -m unittest discover -s tests -v
```


## Model-assisted conversation: steps 16-20

The console creates a `ModelAssistant` and injects it into `TravelBuddy`. The model
receives system instructions, a snapshot of the current step and choices, the
available options, and the conversation history. It supplies short acknowledgments
and travel advice. For unrelated questions, it is instructed to acknowledge briefly
and return to planning; the application always appends the current menu.

Selection matching remains explicit: enter a listed number or full option name.
The model cannot change stored choices. The final summary is generated from those
choices so it remains available even when the API fails. Model wording can vary;
its behavior has been tested using simulated responses, not a live provider call.

Authentication, permission, connection, timeout, rate-limit, credit, model/request,
and service errors produce readable messages without printing raw provider error
bodies. Empty responses also fall back to the guided flow. Users can keep choosing
options after a failed request; later non-exit turns try the model again. The SDK
uses the configured 30-second timeout and up to two retries. No alternate model is
selected automatically; model availability/fallback still needs assignment review.

`exit` skips the API at every stage, including after the summary. EOF and Ctrl+C
end the session with a goodbye, including Ctrl+C while waiting for a model response.
The client is closed when the session ends. Missing configuration still stops startup
with an explanatory message. Live API verification remains pending.
