# typedict for the agent system
# ---------------------------------------------------------------------------
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict

class State(TypeDict):
    messages: Annotated[list[str], add_messages] # Seznam zpráv v konverzaci
    message_type: str | None

