from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import ModelResponse
from state import State
from prompts import promptSystem, promptHuman, promptImage
from prompts import promptTopicHum, promptTopicSys, promptValidator
from openai import OpenAI
import os
from constants import directoryOutput, NUM_IMAGES_TO_ADD
from config import GraphConfig
from langgraph.types import Command
import base64
import uuid



async def STT(state: State) -> Command[Literal["function_calling"]]:    
    prompt = input("Prompt: ")
    print(prompt)
    return Command(
        update={"human_prompt": prompt},
        goto="function_calling"
    )


async def TTS(state: State) -> Command[Literal["router"]]:
    model_prompt = state.model

    
async def router(state:State) -> Command[Literal["END", "TTS"]]:
    if state.actual<=2: 
        goto = "TTS"
    else:
        goto = "END"
    return Command(
        goto=goto
        )


async def function_calling(state: State) -> Command[Literal["VLA", "TTS"]]:
    llm = ChatOpenAI(
        model=GraphConfig().llm_base,
        temperature=GraphConfig().model_temperature
    )
    llm = llm.with_structured_output(ModelResponse)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    chain = prompt | llm
    response = await chain.ainvoke(
        {"seed_value": state.seed, "topic": state.topic}
    ) # what?
    print(f""" -> Creating the schema number {state.number_generations}
    with topic : {state.topic}""")

    response = ModelResponse.model_validate(response)
    output_model: ModelResponse = response
    goto = "VLA"
    return Command(
        update={"": output_model},
        goto=goto
    )


async def VLA(state: State) -> Command[Literal["TTS"]]:
    print("Action")
    return Command(goto="TTS")


async def vision_model(state: State) -> Command[Literal["TTS"]]:
    return Command(goto="TTS")
