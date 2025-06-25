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
import os

def createImage(stringFlowchart: str, name: str, size: str = "1024x1024", quality: str = "standard") -> bool:
    
    """
    Create an image and save it as .png in the images subdirectory

    Args:
        stringFlowchart : str
        name : str (it should include the .png at the end)
        size : str
        quality : str
    """
    try:
        prompt =promptImage + stringFlowchart
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        dir_path = "images"
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, name)
        with open(file_path, 'wb') as f:
            f.write(img_data)
        return True
    except Exception as e:
        print(f"Error creating image: {e}")
        return False

def generate_variants(state: State) -> dict:
    """This probably would need a description such that"""

    llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
    llm = llm.bind_tools([createImage])
    llm = llm.with_structured_output(GeneratorVariantOutput)

    #parser = PydanticOutputParser(pydantic_object = GeneratorVariantOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    
    #chain = prompt | llm | parser
    chain = prompt | llm
    
    #response = chain.ainvoke(input= state.seed)  #await 
    
    result: GeneratorVariantOutput =  chain.invoke({"seed_value":state.seed})
    #response_parsed = GeneratorVariantOutput.model_validate(response) # PydanticOutpaParser do it. Prove!
    
    return {
        "schemas_generations": [result] # "schemas_generations": response_parsed
    }

def route(state: State) -> Literal ["generate_variants","__end__"]:
    return "__end__" if (state["number_generations"] == 2) else "generate_variants"

