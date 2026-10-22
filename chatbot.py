"""Guided trip selection and session history, independent of console and API I/O."""

from dataclasses import dataclass, field
from enum import Enum

TRIP_TYPES = ("Beach getaway", "Mountain adventure", "City break")
ACCOMMODATIONS = ("Hotel", "Hostel", "Vacation rental")
ACTIVITIES = {
    "Beach getaway": ("Swimming", "Snorkeling", "Sunset beach walk"),
    "Mountain adventure": ("Hiking", "Mountain biking", "Stargazing"),
    "City break": ("Museum visit", "Food tour", "Walking tour"),
}


class Step(str, Enum):
    TRIP_TYPE = "trip_type"
    ACCOMMODATION = "accommodation"
    ACTIVITIES = "activities"
    SUMMARY = "summary"
    EXITED = "exited"


@dataclass
class ConversationState:
    step: Step = Step.TRIP_TYPE
    trip_type: str | None = None
    accommodation: str | None = None
    activity: str | None = None
    history: list[dict[str, str]] = field(default_factory=list)


def format_options(question: str, options: tuple[str, ...]) -> str:
    menu = "\n".join(f"{i}. {name}" for i, name in enumerate(options, 1))
    return f"{question}\n{menu}\nEnter an option number or its name, or type exit."


def parse_choice(message: str, options: tuple[str, ...]) -> str | None:
    """Accept only an offered number or full name, ignoring case and whitespace."""
    answer = " ".join(message.split()).casefold()
    for number, option in enumerate(options, 1):
        if answer in (str(number), option.casefold()):
            return option
    return None


def get_startup_message() -> str:
    return (
        "Hi! I'm TravelBuddy. Let's plan your weekend getaway!\n"
        "We'll choose your trip type, accommodation, and activities together.\n"
        "Type exit whenever you want to leave.\n\n"
        + format_options("What kind of trip sounds good?", TRIP_TYPES)
    )


class TravelBuddy:
    def __init__(self):
        self.state = ConversationState()

    def start(self) -> str:
        """Record the greeting once, even if start is called again."""
        if not self.state.history:
            self._reply(get_startup_message())
        return self.state.history[-1]["content"]

    def _reply(self, text: str) -> str:
        self.state.history.append({"role": "assistant", "content": text})
        return text

    def current_options(self) -> tuple[str, ...]:
        if self.state.step == Step.TRIP_TYPE:
            return TRIP_TYPES
        if self.state.step == Step.ACCOMMODATION:
            return ACCOMMODATIONS
        if self.state.step == Step.ACTIVITIES:
            return ACTIVITIES[self.state.trip_type]
        return ()

    def current_prompt(self) -> str:
        questions = {
            Step.TRIP_TYPE: "What kind of trip sounds good?",
            Step.ACCOMMODATION: "Where would you like to stay?",
            Step.ACTIVITIES: f"What would you like to do on your {self.state.trip_type}?",
        }
        return format_options(questions[self.state.step], self.current_options())

    def respond(self, message: str) -> str:
        if self.state.step == Step.EXITED:
            return "This conversation has ended."
        if not self.state.history:
            self.start()
        self.state.history.append({"role": "user", "content": message})
        if message.strip().casefold() == "exit":
            self.state.step = Step.EXITED
            return self._reply("Goodbye! Have a wonderful next adventure!")
        if self.state.step == Step.SUMMARY:
            return self._reply("Your choices are already saved for this session.")

        choice = parse_choice(message, self.current_options())
        if choice is None:
            return self._reply("I didn't recognize that choice. Please choose one of these options.\n" + self.current_prompt())

        if self.state.step == Step.TRIP_TYPE:
            self.state.trip_type = choice
            self.state.step = Step.ACCOMMODATION
            reply = f"Great choice! Your trip type is {choice}.\n\n" + self.current_prompt()
        elif self.state.step == Step.ACCOMMODATION:
            self.state.accommodation = choice
            self.state.step = Step.ACTIVITIES
            reply = f"Your accommodation choice is {choice}.\n\n" + self.current_prompt()
        else:
            self.state.activity = choice
            self.state.step = Step.SUMMARY
            reply = f"Great! You've chosen {choice}. All three choices are saved for this session."
        return self._reply(reply)
