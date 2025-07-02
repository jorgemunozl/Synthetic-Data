from typing import Annotated
from pydantic import BaseModel, Field


class GraphConfig(BaseModel):
    base: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = Field(
        default="gpt-4o",
        description="Base model for graph"
    )
    image: Annotated[str, {"__template_metadata__": {"kind": "imag"}}] = Field(
        default="gpt-image-1",
        description="Base model for graph"
        )
    model_temperature: int = Field(default=1, description="temperature")
