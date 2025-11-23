from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import ModelResponse
from state import State
from config import GraphConfig
from langgraph.types import Command
from cartesia_service import TTSService
from models import Decision


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
        temperature=GraphConfig().model_temperature
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
    print(response)
    print(response.decision)
    if response.decision == Decision.TASK:
        goto = "VLA"
    else:
        goto = "TTS"
    return Command(
        update={"model_response": output_model},
        goto=goto
    )


async def TTS(state: State) -> Command[Literal["router"]]:
    speaker = TTSService(
        api_key="sk_car_Ea5Xgd6vZ5TH8DuNpPuN6q"
    )
    #try:
    #    await speaker.start()
    #finally:
    #    await speaker.close()

    model_prompt = state.model_response
    print(model_prompt.answer)
    return Command(goto="router")


async def router(state: State) -> Command[Literal["__end__", "TTS"]]:
    if state.number_step < 2:
        goto = "STT"
    else:
        goto = "__end__"
    return Command(
        update={"number_step": state.number_step+1},
        goto=goto
        )


async def VLA(state: State) -> Command[Literal["TTS"]]:
    action_prompt = state.model_response
    print("Doing using the prompt", action_prompt)
    return Command(goto="TTS")


#async def vision_model(state: State) -> Command[Literal["TTS"]]:
#    print("Looking")
#    return Command(goto="TTS")
