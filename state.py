from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from typing import Optional, Annotated
from pydantic import BaseModel, Field

from models import NodesVariant
from constants import SeedBase

class GeneratorVariantState(BaseModel):
  name: Optional[str]           = Field(description = "")
  description: Optional[str]    = Field(description = "")
  startNode: Optional[str]      = Field(description = "")
  nodes: Optional[NodesVariant] = Field(description = "")
  edges: Optional[str]          = Field(description = "")

# Class create only for State

class State(BaseModel):
  messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory = list,
        description = "The history of messages",
  )
  seed: str = Field(default = SeedBase.model_json_schema(), description = "Seed base who is gonna to be the model")
  number_generations: int = Field(default = 3, description = "Number of images")
  schemas_generations: list[GeneratorVariantState] = Field(
    default_factory = list,
    description = "Here is where all the json are gonna be saved"
  ) 
