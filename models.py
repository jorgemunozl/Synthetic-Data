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
    text: str = Field(description="freedom")
    x : int = Field(description="")
    y : int = Field(description="")
    width : int = Field(description="")
    height : int = Field(description="")


class ConditionOptionsEnum(str, Enum):
    YES = "YES"
    NO = "NO"


class sides(str,Enum):
    bottom = "bottom"
    top    = "top"
    left   = "left"
    right  = "right"


class EdgesVariant(BaseModel):
    id: str = Field(description="")
    from_: str = Field(description="")
    to: str = Field(description="")
    label: Optional[ConditionOptionsEnum] = Field(description="")
    fromSide : sides = Field(description="")
    toSide : sides = Field(description="")

class GeneratorVariantOutput(BaseModel):
    name: str = Field(description="")
    description: str = Field(description="")
    startNode: str = Field(description="")
    nodes: list[NodesVariant] = Field(default_factory=list, description="")
    edges: list[EdgesVariant] = Field(default_factory=list, description="")
