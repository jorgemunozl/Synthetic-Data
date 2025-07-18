from typing import Annotated
from pydantic import BaseModel, Field
from constants import topics



class GraphConfig(BaseModel):
    modelBase: Annotated[str, {}] = Field(
        default="gpt-4o",
        description="Model for planner and generator nodes"
    )
    temperature: Annotated[float, {}] = Field(
        default=0,
        description="Temperature for all the models"
    )
    modelReasoning: Annotated[str, {}] = Field(
        default="o4-mini",
        description="Model for the reflector node"
    )
    threshold: Annotated[float, {}] = Field(
        default=0.8,
        description="Threshold that reflector is gonna to use"
    )
    difficultyStep: Annotated[int, {}] = Field(
        default=1,
        description="Number of flowcharts to jump of difficulty"
    )
    topics: Annotated[list, {}] = Field(
        default=topics,
        description="Model topics for the flowcharts"
    )
    recursionLimit: Annotated[int, {}] = Field(
        default=2,
        description="Model topics for the flowcharts"
    )
