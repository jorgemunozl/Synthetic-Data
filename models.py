from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class NodeTypesEnum(str, Enum):
    START = "start"
    DECISION = "decision"
    TASK = "task"
    END = "end"

class ConditionOptionsEnum(str, Enum):
    YES = "yes"
    NO = "no"

class NodesVariant(BaseModel):
    id: str = Field(description="")
    type: NodeTypesEnum = Field(description="")
    label: str = Field(description="")

class EdgesVariant(BaseModel):
    id: str = Field(description="")
    from: str = Field(description="")
    to: str = Field(description="")
    condition: Optional[ConditionOptionsEnum] = Field(description="")

class GeneratorVariantOutput(BaseModel):
    name: str = Field(description="")
    description: str= Field(description="")
    startNode: str= Field(description="")
    nodes: NodesVariant= Field(description="")
    edges: str= Field(description="")