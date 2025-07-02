from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from models import NodesVariant, EdgesVariant, GeneratorVariantOutput  # Import from models only
from constants import SeedBase


class GeneratorVariantState(BaseModel):
  name: Optional[str] = Field(description="a")
  description: Optional[str]= Field(description = "")
  startNode: Optional[str]= Field(description = "")
  nodes: list[NodesVariant]= Field(
    default_factory = list, 
    description = "list of NodesVariant")
  edges: list[EdgesVariant]     = Field(
    default_factory = list,
    description = "list of EdgesVariant")

# Removed duplicate GeneratorVariantOutput definition

class State(BaseModel):
  messages: Annotated[list[BaseMessage], add_messages] = Field(
  default_factory = list,
  description = "The history of messages"
  )
  seed: str = Field(default = str(SeedBase.model_json_schema()), description = "Example of how the model should do it")
  number_generations: int = Field(default = 3, description = "Number of images")
  schemas_generations: list[GeneratorVariantOutput] = Field(
    default_factory = list,
    description = "Here is where all the json are gonna be saved"
  )
