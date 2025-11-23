from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import ModelResponse
from state import State
from config import GraphConfig
from langgraph.types import Command
from cartesia_service import TTSService, STTService
from models import Decision
import asyncio


async def text_generator(answer: str):
    # Split on punctuation but preserve it
    import re
    chunks = re.split(r'([.!?\n])', answer)

    buffer = ""
    for part in chunks:
        if part.strip() == "":
            continue

        buffer += part

        # if this part ends a sentence, yield it
        if part in ".!?\n":
            yield buffer
            buffer = ""

    # leftover
    if buffer.strip():
        yield buffer

    # allow async systems to breathe
    await asyncio.sleep(0)


async def STT(state: State) -> Command[Literal["function_calling"]]:
    #speaker = TTSService(
    #    api_key="sk_car_Ea5Xgd6vZ5TH8DuNpPuN6q"
    #)
    #streamer = STTService(
    #    api_key="sk_car_Ea5Xgd6vZ5TH8DuNpPuN6q"
    #)
    #try:
    #    async for text in streamer.start_stream():
    #        print(f"{text}")
    #finally:
    #    await streamer.close()
    prompt = input("Prompt: ")
    print(prompt)
    return Command(
        update={"human_prompt": prompt},
        goto="function_calling"
    )


async def function_calling(state: State) -> Command[Literal["VLA", "TTS"]]:
    llm = ChatOpenAI(
        model=GraphConfig().llm_base,
        temperature=GraphConfig().model_temperature,
    )
    llm = llm.with_structured_output(ModelResponse)
    prompt = ChatPromptTemplate.from_messages([
        ("system", GraphConfig().prompt_system),
        ("human", state.human_prompt)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({})
    print("Generating the model response")
    response = ModelResponse.model_validate(response)
    output_model: ModelResponse = response
    entry = ""
    if response.decision == Decision.TASK:
        goto = "VLA"
    else:
        entry = output_model.answer
        goto = "TTS"
    return Command(
        update={"model_response": output_model, "text_entry": entry},
        goto=goto
    )


async def TTS(state: State) -> Command[Literal["router"]]:
    speaker = TTSService(
        api_key="sk_car_Ea5Xgd6vZ5TH8DuNpPuN6q"
    )
    gen = text_generator(state.text_entry)
    try:
        await speaker.start(gen)
    finally:
        await speaker.close()

    return Command(goto="router")


async def router(state: State) -> Command[Literal["__end__", "STT"]]:
    if state.number_step < 2:
        goto = "STT"
    else:
        goto = "__end__"
    return Command(
        update={"number_step": state.number_step+1},
        goto=goto
        )


async def VLA(state: State) -> Command[Literal["supervisor"]]:
    print("Doing task: ", state.model_response.prompt_task)
    # Assume that it did it well.
    return Command(goto="supervisor")


async def supervisor(state: State) -> Command[Literal["TTS"]]:
    llm = ChatOpenAI(
        model=GraphConfig().llm_base,
        temperature=GraphConfig().model_temperature,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", GraphConfig().prompt_system_supervisor),
        ("human", state.human_prompt)
    ])
    chain = prompt | llm
    print("Generating the model response")
    response = await chain.ainvoke({})
    parse_response = response.content
    print(parse_response)
    return Command(
        update={"text_entry": parse_response},
        goto="TTS",
    )
