from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import ModelResponse
from state import State
from config import GraphConfig
from langgraph.types import Command
from cartesia_service import TTSService
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
    tts = ""
    if response.decision == Decision.TASK:
        goto = "VLA"
    else:
        tts = output_model.answer
        goto = "TTS"
    return Command(
        update={"model_response": output_model,
                "tts": tts},
        goto=goto
    )


async def TTS(state: State) -> Command[Literal["router"]]:
    speaker = TTSService(
        api_key="sk_car_Ea5Xgd6vZ5TH8DuNpPuN6q"
    )
    gen = text_generator(state.tts)
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
    # Gemini-Model
    system_text = """
        You are a supervisor assistant.
        The VLA Model executed a task for the user.
        Generate a concise user-facing answer describing what was done
        and the result.
    """
    human_text = f"""
    User request: {state.human_prompt}
    Task performed by VLA: {state.model_response.prompt_task}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("human", human_text),
    ])

    chain = prompt | llm
    print("Supervisor: generating final answer...")
    response = await chain.ainvoke({})

    # Normalize response to a plain string for TTS and the State model
    if hasattr(response, "content"):
        tts_text = response.content
    elif isinstance(response, dict):
        # try to get common keys
        tts_text = (
            response.get("answer")
            or response.get("content")
            or str(response)
        )
    else:
        tts_text = str(response)

    # Update the structured model_response as well
    output_model = ModelResponse(
        decision=Decision.NO_TASK,
        answer=str(tts_text),
    )

    return Command(
        update={"model_response": output_model, "tts": tts_text},
        goto="TTS",
    )

# async def vision_model(state: State) -> Command[Literal["TTS"]]:
#     print("Looking")
#     return Command(goto="TTS")
