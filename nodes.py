from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


from models import GeneratorVariantOutput
from constants import SeedBase
from state import State
from config import GraphConfig

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

# THINK IT LIKE FOLLOW: GENERATE VARIANTS IS A MODEL ITSELF COMPLETELY INDEPEDENT AND SEPARATE FROM THE GRAPH!
#async
def generate_variants(state: State, *, config: RunnableConfig) -> dict:

    llm = ChatOpenAI(model = GraphConfig.base_model, temperature = 0).with_structured_output(GeneratorVariantOutput)
    
    parser = PydanticOutputParser(pydantic_object = GeneratorVariantOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Please output the seed variant wrapped in ```json``` fences."),
        ("system", parser.get_format_instructions()),
        ("human", f"Create one example of the follow seed {state.seed}")
    ])
    
    chain = prompt | llm | parser

    #response = chain.ainvoke(input= state.seed)  await 
    result: GeneratorVariantOutput =  chain.ainvoke({"query":state.seed})

    #response_parsed = GeneratorVariantOutput.model_validate(response) # PydanticOutpaParser do it. Prove!
    
    return {
        "schemas_generations": result # "schemas_generations": response_parsed
    }

# If is asynchronic then it create the n json is one shot. There is no need from a bucle! First let's do it
# only with one example. One step at a time.

# So it returns a dict of one element, key string and value Generatorvariantoutput. 
# def route(state: State) -> Literal ["callingGPT4","__end__"]:

#    return "__end__" if (state["count"] == numImages) else "callingGPT4"
