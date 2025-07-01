from typing import Annotated
from pydantic import BaseModel, Field


class GraphConfig(BaseModel):
    base_model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = Field(
        default="gpt-4o",
        description="Base model for graph"
    )
    image_model: Annotated[str, {"__template_metadata__": {"kind": "image_model"}}] = Field(
        default="gpt-image-1",
        description="Base model for graph"
        )
