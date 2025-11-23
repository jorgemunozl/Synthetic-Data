from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Annotated
from pydantic import BaseModel, Field
from models import ModelResponse, Decision


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="Conversation history messages",
    )
    tts: str = Field(
        default="",
        description=""
    )
    number_step: int = Field(
        default=0,
        description="Total number of generations"
    )
    human_prompt: str = Field(
        default="",
        description="Init of the loop, the human say the beginnig."
    )
    model_response: ModelResponse = Field(
        default_factory=lambda: ModelResponse(decision=Decision.NO_TASK),
        description="Init of the loop, the human say the beginnig."
    )
