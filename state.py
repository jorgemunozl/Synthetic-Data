from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from .models import NodesVariant
from .constants import SeedData
class GeneratorVariantState(BaseModel):
    name: Optional[str] = Field(description="")
    description: Optional[str]= Field(description="")
    startNode: Optional[str]= Field(description="")
    nodes: Optional[NodesVariant]= Field(description="")
    edges: Optional[str]= Field(description="")

class State(BaseModel):

  messages: Annotated[list[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="The history of messages",
  )
  seed: str = Field(default=SeedData.model_schema_json(), description="")
  number_generations: int = Field(default=3, description="")
  schemas_generations: list[GeneratorVariantState] = Field(default_factory=list, description="")
