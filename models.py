from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class NodeTypesEnum(str, Enum):
    START = "start"
    DECISION = "decision"
    TASK = "task"
    END = "end"


class NodesVariant(BaseModel):
    id: str = Field(description="a")
    type: NodeTypesEnum = Field(description="")
    label: str = Field(description="freedom")


class ConditionOptionsEnum(str, Enum):
    YES = "yes"
    NO = "no"


class EdgesVariant(BaseModel):
    id: str = Field(description="")
    from_: str = Field(description="")
    to: str = Field(description="")
    condition: Optional[ConditionOptionsEnum] = Field(description="")


class GeneratorVariantOutput(BaseModel):
    name: str = Field(description="")
    description: str = Field(description="")
    startNode: str = Field(description="")
    nodes: list[NodesVariant] = Field(default_factory=list, description="")
    edges: list[EdgesVariant] = Field(default_factory=list, description="")
