from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from models import NodesVariant, EdgesVariant
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
    actual_number: int = Field(default=0,
                               description="Current generation index")
    topic: str = Field(default=str("Flowchart about probability theory"),
                       description="Current topic")
    schemas_generations: list[dict] = Field(
        default_factory=list,
        description="List of all generated schema variants",
    )
    pathToImage: str = Field(description="path to image to review")
    score: float = Field(default=0.0, description="score for the image")
    threshold: float = Field(default=0.0,
                             description="If it is more than 0.9 then it's accepted")
    modification: str = Field(default="",description="what is gonna to be modified")
    recursionLimit: int = Field(default=2,description="How much times how maximun a image can be improved")