from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Annotated
from pydantic import BaseModel, Field
from constants import topics, difficulty


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="Conversation history messages",
    )
    seed: str = Field(
        default=str(""),
        description="Seed value for generation",
    )
    number_generations: int = Field(default=0,
                                    description="Total number of generations")
    actual_number: int = Field(default=0,
                               description="Current generation index")
    topic: list = Field(default=topics,
                        description="Current topic")
    plannerOutput: str = Field(default="")
    generatorOutput: str = Field(default="")
    difficulty: list = Field(default=difficulty)
    recursion: int = Field(default=0)
    schemas_generations: list[dict] = Field(
        default_factory=list,
        description="List of dicts id-mermaid",
    )
    score: float = Field(default=0.0, description="score for the image")
