from typing import Annotated
from pydantic import BaseModel, Field


class GraphConfig(BaseModel):
    llm_base: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = Field(
        default="gpt-4o",
        description="Base language model for function calling"
    )
    model_temperature: int = Field(default=1, description="temperature")
