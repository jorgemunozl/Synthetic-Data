from typing import Annotated
from pydantic import BaseModel, Field


class GraphConfig(BaseModel):
    base_model: Annotated[str, {"__template_metadata__":{"kind": "llm"}}]= Field(
        default="gpt-4.1",
        description="base model for graph"
    )