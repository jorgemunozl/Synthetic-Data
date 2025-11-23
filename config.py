from typing import Annotated
from pydantic import BaseModel, Field


model_prompt = """
    You are a helpful Vision Language Action model, you have a physical body,
    specifically two robotic arms. When the user wants you to perform a
    task, reply with decision 'TASK' and provide a high level prompt describing
    how to resolve it. Otherwise reply with decision 'NO_TASK' and provide a
    natural language answer. If you already did it, say it to the user.
"""


class GraphConfig(BaseModel):
    llm_base: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = Field(
        default="gpt-4o",
        description="Base language model for function calling"
    )
    model_temperature: int = Field(default=1, description="temperature")
    prompt_system: str = model_prompt
    prompt_system_supervisor: str = "eso"
