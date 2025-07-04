from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from models import NodesVariant, EdgesVariant, GeneratorVariantOutput
from constants import SeedBase


class GeneratorVariantState(BaseModel):
    name: Optional[str] = Field(description="Name of the variant")
    description: Optional[str] = Field(description="Description variant")
    startNode: Optional[str] = Field(description="ID of the starting node")
    nodes: list[NodesVariant] = Field(
        default_factory=list,
        description="List of node objects in the variant",
    )
    edges: list[EdgesVariant] = Field(
        default_factory=list,
        description="List of edge objects in the variant",
    )


class State(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="Conversation history messages",
    )
    seed: str = Field(
        default=str(SeedBase.model_json_schema()),
        description="Seed value for generation",
    )
    number_generations: int = Field(default=0,
                                    description="Total number of generations")
    number_actual: int = Field(default=0,
                               description="Current generation index")
    schemas_generations: list[GeneratorVariantOutput] = Field(
        default_factory=list,
        description="List of all generated schema variants",
    )
