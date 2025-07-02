from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import GeneratorVariantOutput
from state import State
from prompts import promptSystem, promptHuman, promptImage
import base64
from openai import OpenAI
import os
from constants import directoryOutput, NUM_IMAGES_TO_ADD, NUM_IMAGE_WE_HAVE
from config import GraphConfig


async def generate_variants(state: State, *, config) -> dict:

    llm = ChatOpenAI(model=GraphConfig().base_model, temperature=0)
    llm = llm.with_structured_output(GeneratorVariantOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    chain = prompt | llm

    output_model: GeneratorVariantOutput = await chain.ainvoke({"seed_value": state.seed}) 

    # Ensure schemas_generations is a flat list of GeneratorVariantOutput models
    updated = list(state.schemas_generations)  # copy existing list
    # Always append as a model instance
    updated.append(GeneratorVariantOutput.model_validate(output_model))
    return {"schemas_generations": updated}
    

def route(state: State) -> Literal["generate_variants", "__end__"]:
    if (state.number_generations == (NUM_IMAGES_TO_ADD+NUM_IMAGE_WE_HAVE)):
        return "__end__"
    else:
        return "generate_variants"


def createImage(state: State) -> dict:    
    
    print("SECOND FUNCTION -------------")
    print(state.number_generations)
    print(state.schemas_generations)
    variant = state.schemas_generations[state.number_generations]
    variant = variant.model_dump()
    prompt = promptImage(variant)
    print("Creating the image")
    client = OpenAI()
    response = client.images.generate(
        model=GraphConfig().image_model,
        prompt=prompt,
        )
    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    
    dir_path = directoryOutput
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{state.number_generations}.png")
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    return {"number_generations": state.number_generations+1}
