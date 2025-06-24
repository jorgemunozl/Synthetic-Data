from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
#from .models import GeneratorVariantOutput
#from .constants import SeedBase

def createImage(prompt: str, name: str, size: str = "1024x1024", quality: str = "standard") -> bool:
    """
    Create an image and save it as .png in the images subdirectory

    Args:
        prompt : str
        name : str (it should include the .png at the end)
        size : str
        quality : str
    """
    try:
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

def createFile(text: str, namefile: str) -> bool:
    """
    Saves a string as a .txt in the prompts subdirectory

    Args:
        text: str
        namefile: str 
    """
    try:
        dir_path = "prompts"
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, namefile)
        with open(file_path, "w") as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error creating file: {e}")
    return False

def readJson():
    pass

def createJson(info: dict, namefile: str) -> bool:
    """
    Saves a dict as a .json in the "jsons" subdirectory

    Args:
        info : dict
        namefile: str (ends in json)
    """
    try:
        dir_path = "jsons"
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, namefile)
        with open(file_path, "w") as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error creating file: {e}")
    return False

"""

async def generate_variants(state: State, *, config: RunnableConfig) -> dict:
    llm = ChatOpenAI(model=config.base_model, temperature=0).with_structured_output(GeneratorVariantOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", ""
            Crea 10 ejemplos mas del siguiente seed {seed}
        ""),
        ("human", "")
    ])
    
    chain = llm | prompt
    response = chain.ainvoke(
        input= state.seed
    )

    response_parsed = GeneratorVariantOutput.model_validate(response)
    
    return {
        "schemas_generations": response_parsed
    }

"""

def route(state: State) -> Literal ["callingGPT4","__end__"]:

    return "__end__" if (state["count"] == numImages) else "callingGPT4"
