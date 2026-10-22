"""Conversation state and the first trip-planning step (no console or API I/O)."""

from dataclasses import dataclass, field
from enum import Enum

TRIP_TYPES = ("Beach getaway", "Mountain adventure", "City break")


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


def get_startup_message() -> str:
    options = "\n".join(f"{i}. {name}" for i, name in enumerate(TRIP_TYPES, 1))
    return (
        "Hi! I'm TravelBuddy. Let's plan your weekend getaway!\n"
        "We'll choose your trip type, accommodation, and activities together.\n"
        "Type exit whenever you want to leave.\n\n"
        "What kind of trip sounds good?\n" + options +
        "\nEnter an option number or its name."
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

    def respond(self, message: str) -> str:
        """Save a trip choice; subsequent planning stages come in later steps."""
        if self.state.step == Step.EXITED:
            return "This conversation has ended."
        if not self.state.history:
            self.start()
        self.state.history.append({"role": "user", "content": message})
        answer = message.strip().casefold()
        if answer == "exit":
            self.state.step = Step.EXITED
            return self._reply("Goodbye! Have a wonderful next adventure!")
        if self.state.step != Step.TRIP_TYPE:
            return self._reply("Your trip type is saved. Accommodation selection is coming next.")
        for number, trip_type in enumerate(TRIP_TYPES, 1):
            if answer in (str(number), trip_type.casefold()):
                self.state.trip_type = trip_type
                self.state.step = Step.ACCOMMODATION
                return self._reply(
                    f"Great choice! Your trip type is {trip_type}.\n"
                    "Your choice is saved for this session. Accommodation selection is coming next."
                )
        return self._reply("Please choose 1, 2, or 3, enter the option's name, or type exit.")
