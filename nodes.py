from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import GeneratorVariantOutput
from state import State
from prompts import promptSystem, promptHuman, promptImage
import base64
from openai import OpenAI
import os
from constants import directoryOutput, NUM_IMAGES_TO_ADD
from config import GraphConfig

"""
store: dict[str, BaseChatMessageHistory] = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()  # implement BaseChatMessageHistory
    return store[session_id]
"""


async def generate_variants(state: State, *, config) -> dict:

    llm = ChatOpenAI(model=GraphConfig().base,
                     temperature=GraphConfig().model_temperature)
    llm = llm.with_structured_output(GeneratorVariantOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    chain = prompt | llm

    """
    chain_with_memory = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="seed_value",
        history_messages_key="messages"
    )
    response = await chain_with_memory.ainvoke(
        {"seed_value": state.seed},
        config={"configurable": {"session_id": "session_2"}}
        )
    """
    print(f" -> Creating the schema number {state.number_generations}")
    response = await chain.ainvoke(
        {"seed_value": state.seed},
        # config={"configurable": {"session_id": "session_2"}}
        )
    response = GeneratorVariantOutput.model_validate(response)
    output_model: GeneratorVariantOutput = response
    updated = list(state.schemas_generations)
    updated.append(GeneratorVariantOutput.model_validate(output_model))

    print(f" -> Schema number {state.number_generations} created")
    return {"schemas_generations": updated}


def route(state: State) -> Literal["generate_variants", "__end__"]:
    if (state.number_generations == (state.number_generations-1+NUM_IMAGES_TO_ADD)):
        return "__end__"
    else:
        return "generate_variants"


def createImage(state: State) -> dict:
    variant = state.schemas_generations[state.number_generations]
    variant = variant.model_dump()
    prompt = promptImage(variant)
    print(f" -> Creating the image number {state.number_generations}")
    """
    client = OpenAI()
    response = client.images.generate(
        model=GraphConfig().image,
        prompt=prompt,
        )
    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    dir_path = directoryOutput
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{state.number_generations}.png")
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    """
    print(f" -> Image number {state.number_generations} created")
    return {"number_generations": state.number_generations+1}
