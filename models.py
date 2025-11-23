from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class Decision(str, Enum):
    """Possible routing decisions returned by the LLM."""
    TASK = "TASK"
    NO_TASK = "NO_TASK"


class ModelResponse(BaseModel):
    """Structured response expected from the LLM."""
    decision: Decision
    prompt_task: Optional[str] = None
    answer: Optional[str] = None
