from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Annotated
from pydantic import BaseModel, Field


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="Conversation history messages",
    )
    number_generations: int = Field(default=0,
                                    description="Total number of generations")
    plannerOutput: str = Field(default="")
    generatorOutput: str = Field(default="")
    evalSheet: str = Field(default="")
    recursion: int = Field(default=0)
    schemas_generations: list[dict] = Field(
        default_factory=list,
        description="List of dicts id-mermaid",
    )
    imagesGenerated: list[str] = Field(
        default_factory=list,
        description="routesToImages"
    )
    mermaidGenerated: list[str] = Field(
        default_factory=list,
        description="MermaidCode"
    )
    promptUser: str = Field(default="")
    diffUser: str = Field(default="")


class ReflectionOutput(BaseModel):
    feedback: str = Field(description="Detailed feedback about the flowchart")
    score: float = Field(
        description="Score from 0.0 to 1.0 indicating quality of the flowchart"
    )
