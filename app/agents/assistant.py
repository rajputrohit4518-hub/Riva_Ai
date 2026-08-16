from agents import Agent

from app.core.identity import IDENTITY
from app.tools.calculator import calculate


def create_riva_agent() -> Agent:
    return Agent(
        name=IDENTITY.name,
        instructions=(
            "You are Riva, a personal AI assistant. "
            "Be helpful, accurate, concise, and action-oriented. "
            "Use available tools when appropriate. "
            "Never claim an action was completed unless it actually succeeded."
        ),
        tools=[calculate],
    )
