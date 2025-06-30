from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import GeneratorVariantOutput
from state import State
from prompts import promptSystem, promptHuman, promptImage
import requests
from openai import OpenAI
import os
from constants import directoryOutput, NUM_IMAGES_TO_ADD, NUM_IMAGE_WE_HAVE
from config import GraphConfig


async def generate_variants(state: State, *, config) -> dict:
    llm = ChatOpenAI(model=GraphConfig.base_model, temperature=0)
    llm = llm.with_structured_output(GeneratorVariantOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    chain = prompt | llm
    result: GeneratorVariantOutput = await chain.ainvoke({"seed_value": state.seed}) 
    lst = state["schemas_generations"].copy()  
    lst.append(result)
    return {"schemas_generations": lst}    
    

def route(state: State) -> Literal["generate_variants", "__end__"]:
    if (state.number_generations == (NUM_IMAGES_TO_ADD+NUM_IMAGE_WE_HAVE+1)):
        return "__end__"
    else:
        return "generate_variants"


def createImage(state: State) -> dict:
    flowchartInfo = state.schemas_generations[0]
    flowchartInfo = flowchartInfo.model_dump()
    flowchartInfo = GeneratorVariantOutput.model_validate(flowchartInfo)
    prompt = promptImage(flowchartInfo)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.images.generate(
        model=GraphConfig.image_model,
        prompt=prompt,
        n=1)
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    dir_path = directoryOutput
    os.makedirs(dir_path, exist_ok=True)
    name = str(state.number_generations) + ".png"
    file_path = os.path.join(dir_path, name)

    with open(file_path, 'wb') as f:
        f.write(img_data)
    return {"number_generations": state.number_generations+1}
