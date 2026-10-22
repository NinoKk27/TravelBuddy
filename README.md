# TravelBuddy

A Python console assistant for planning a weekend getaway. Choose a trip type,
accommodation, and a matching activity. OpenRouter provides brief acknowledgments,
travel advice, and help returning to the current question.

## Setup and run

Use Python 3.11 or newer. In the project folder, create a virtual environment if
you do not already have one, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Copy the environment template only if `.env` does not already exist. Edit `.env`
locally and replace the placeholder API key with your OpenRouter key. Set
`OPENROUTER_MODEL` to the exact model required by your assignment. The template's
model availability has not been verified. If it is unavailable, select a currently
available free model in OpenRouter and put its exact model ID in this setting.
Model switching is manual; the application does not silently choose another model.

```powershell
.\.venv\Scripts\python.exe main.py --check-api
.\.venv\Scripts\python.exe main.py
```

The first command sends one short live request and exits. Normal conversations send
requests after non-exit answers. In PyCharm, select `.venv` as the project interpreter
and run `main.py`. Settings are loaded from the `.env` beside the source files, even
when the working directory differs. Existing environment variables take precedence.
Keep `.env` out of Git and do not share your key in chat.

## Using the planner

Enter a displayed number or the full option name. Matching ignores case and extra
whitespace. Invalid choices repeat the current menu without changing saved choices.

| Stage | Options |
| --- | --- |
| Trip type | Beach getaway; Mountain adventure; City break |
| Accommodation | Hotel; Hostel; Vacation rental |
| Beach activity | Swimming; Snorkeling; Sunset beach walk |
| Mountain activity | Hiking; Mountain biking; Stargazing |
| City activity | Museum visit; Food tour; Walking tour |

After the third selection, the bot displays the exact saved plan and accepts
follow-up questions. Type `exit` at any stage to say goodbye. EOF or Ctrl+C also
ends the session. Choices and history exist only in memory and reset on restart.
The bot does not book travel, check live availability, or persist plans.

## Example conversation

This transcript is generated from the actual conversation engine with model replies
disabled (`TravelBuddy()`). Live runs add model-generated text before these menus
and confirmations; that wording has not been verified against a live provider.

```text
Hi! I'm TravelBuddy. Let's plan your weekend getaway!
We'll choose your trip type, accommodation, and activities together.
Type exit whenever you want to leave.

What kind of trip sounds good?
1. Beach getaway
2. Mountain adventure
3. City break
Enter an option number or its name, or type exit.
You: 2
Great choice! Your trip type is Mountain adventure.

Where would you like to stay?
1. Hotel
2. Hostel
3. Vacation rental
Enter an option number or its name, or type exit.
You: 3
Your accommodation choice is Vacation rental.

What would you like to do on your Mountain adventure?
1. Hiking
2. Mountain biking
3. Stargazing
Enter an option number or its name, or type exit.
You: 1
Here's your weekend plan!
Trip type: Mountain adventure
Accommodation: Vacation rental
Activity: Hiking
Your choices are saved for this session. Ask a travel question or type exit to leave.
You: exit
Goodbye! Have a wonderful next adventure!
```

## Structure and design decisions

- `main.py`: console I/O, startup validation, client lifetime, and the API-check command.
- `config.py`: immutable settings, environment loading, and validation. The settings
  representation hides the key; blank values and the example key are rejected.
- `chatbot.py`: conversation state, option parsing, history, prompts, and summaries.
- `llm_client.py`: OpenRouter client, requests, and readable failure messages.
- `tests/`: offline unit and console-flow tests using simulated model responses.

The state advances from `TRIP_TYPE` to `ACCOMMODATION`, `ACTIVITIES`, and `SUMMARY`.
`EXITED` can be reached from any stage. Only valid explicit choices advance the
state. Earlier choices are preserved when input is invalid or a request fails.

The model adapter is injected into the conversation engine. The engine has no
SDK dependency, network operations, or console I/O. This separation allows offline
testing. It is a small modular application rather than a full layered Clean
Architecture project.

Each request contains system instructions, the current state and available options,
and a snapshot of the conversation history. The model is instructed to give concise
travel advice and redirect unrelated questions. The application appends its own menu
or summary and never lets model text modify the stored choices. Model wording can
still vary or be inaccurate; live behavior requires checking with the chosen model.

## Errors and troubleshooting

- Missing configuration: startup stops with the setting name that needs attention.
- Authentication or permission error: check the key and account/model access.
- Unavailable model or invalid request: check the configured model ID.
- Insufficient credits: check the account balance or select an available free model.
- Rate limit, timeout, or service error: try again later.
- Connection error: check internet access.
- Empty model response: the guided planner continues with its own menu or summary.

Errors do not print raw provider response bodies. During a conversation, expected API
failures produce a readable message and preserve the guided flow. Later non-exit turns
try the model again. The SDK has a 30-second request timeout and up to two retries,
so a failed turn can take longer than 30 seconds. `exit` does not call the model.
The client is closed when the session ends.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests run offline without a real key or API requests. They cover all 27 choice
combinations, case and whitespace handling, invalid inputs at every stage,
trip-specific activities, state/history isolation, summaries, unrelated messages,
model request context, API failures, exits, console interruption, configuration,
and client cleanup. Top-level dependencies are pinned to the locally tested versions.

## Requirements review and remaining verification

The checklist below uses the original project README as the working specification.
The separate programming assignment was not found in the supplied Exercise2 folder;
its exact model, required option wording, and submission rules remain unconfirmed.

| Requirement | Result |
| --- | --- |
| Friendly greeting | Implemented |
| Three options at each planning stage | Implemented |
| Activities appropriate to trip type | Implemented |
| Preserve history and prior choices | Implemented per session |
| Handle unexpected input and return to the current step | Implemented; model wording tested with simulated responses |
| Final plan summary | Implemented from saved choices |
| Goodbye and exit | Implemented at all stages |
| Specified model or free alternative | Configurable; manual replacement documented, exact required model unconfirmed |
| Live API verification | Blocked by missing OPENROUTER_API_KEY at final review |
| Original-assignment compliance | Pending original assignment |

Before submission, configure the key locally, verify the model with `--check-api`,
then try a full live conversation including an unrelated question. Compare the
result and model choice with the original assignment. The offline checks cannot
confirm credentials, current model availability, or the quality of live responses.

## Git

The repository is https://github.com/NinoKk27/TravelBuddy. `.env`, `.venv`, `.idea`,
and Python cache files are ignored. Review the diff before committing; include
source, tests, README, requirements, and `.env.example`, but never credentials.
