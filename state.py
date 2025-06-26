from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from models import NodesVariant, EdgesVariant
from constants import SeedBase

class GeneratorVariantState(BaseModel):
  name: Optional[str]           = Field(description = "")
  description: Optional[str]    = Field(description = "")
  startNode: Optional[str]      = Field(description = "")
  nodes: list[NodesVariant]     = Field(
    default_factory = list, 
    description = "list of NodesVariant")
  edges: list[EdgesVariant]     = Field(
    default_factory = list,
    description = "list of EdgesVariant")

class GeneratorVariantOutput(BaseModel):
    name: str = Field(description="")
    description: str = Field(description="")
    startNode: str = Field(description="")
    nodes: list[NodesVariant] = Field(default_factory = list,description="")
    edges: list[EdgesVariant] = Field(default_factory = list,description="")

class State(BaseModel):
  messages: Annotated[list[BaseMessage], add_messages] = Field(
  default_factory = list,
  description = "The history of messages"
  )
  seed: str = Field(default = SeedBase.model_json_schema(), description = "Example of how the model would do it")
  number_generations: int = Field(default = 3, description = "Number of images")
  schemas_generations: list[GeneratorVariantOutput] = Field(
    default_factory = list,
    description = "Here is where all the json are gonna be saved"
  ) 
