from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from typing_extensions import Literal
from models import GeneratorVariantOutput
from constants import SeedBase
from state import State
from config import GraphConfig
from prompts import *
import requests
from openai import OpenAI
import os
from constants import directoryOutput, NUM_IMAGES_TO_ADD, NUM_IMAGE_WE_HAVE 

async def generate_variants(state: State,*, config) -> dict:


    llm = ChatOpenAI(model = "gpt-4o", temperature = 0).with_structured_output(GeneratorVariantOutput)
    #parser = PydanticOutputParser(pydantic_object = GeneratorVariantOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    #chain = prompt | llm | parser
    chain = prompt | llm
    #response = chain.ainvoke(input= state.seed)  # 
    result: GeneratorVariantOutput = await chain.ainvoke({"seed_value":state.seed})

    return {"schemas_generations":  [result.model_dump()]}
    
    """
    lst = state["schemas_generations"].copy()  # or use the existing list
    lst.append(result)
    return {"schemas_generations": lst}
    """

def route(state: State) -> Literal ["generate_variants","__end__"]:
    if (state.number_generations == (NUM_IMAGES_TO_ADD + NUM_IMAGE_WE_HAVE + 1 )):
        return "__end__" 
    else:
        return "generate_variants"

def createImage(state: State) -> dict:
    flowchartInfo = state.schemas_generations[0]
    flowchartInfo = flowchartInfo.model_dump()
    flowchartInfo = GeneratorVariantOutput.model_validate(flowchartInfo)
    flowchartInfo = flowchartInfo.model_dump_json(indent = 2)
    prompt = promptImage + flowchartInfo
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.images.generate(
        model="dall-e-3",
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
    
    return {"number_generations" : state.number_generations+1}
    