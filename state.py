from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Annotated
from pydantic import BaseModel, Field
from models import ModelResponse


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="Conversation history messages",
    )
    number_step: int = Field(
        default=0,
        description="Total number of generations"
    )
    human_prompt: str = Field(
        default=0,
        description="Init of the loop, the human say the beginnig."
    )
    model_response: ModelResponse = Field(
        default=0,
        description="Init of the loop, the human say the beginnig."
    )
