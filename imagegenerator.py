import os, getpass
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command
from typing_extensions import Literal
from langgraph.prebuilt import ToolNode, tools_condition
import requests
from openai import OpenAI

# prompt => string template con variables, basado en formato ninja => prompt1: "mi nombre es {name}" => prompt1.name = joel => prompt1 = "mi nombre es joel"
# output_parsers => structured output => "oye analiza si el comprador esta molesto o feliz, pero respondeme de la siguiente forma '{response: "feliz"}'" => "{response: triste}"
# llm => packages ya listos de los models para consumirlos => axios.post ("https://api.openai.com/")
# chain (runnable) => llm + output parser. + prompt =>
# tools => function calling => brinda las definiciones => una tool es una function que lo que hace es decirle al modelo que datos ingresa y que datos exactos quiere que retorne,

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

listTool = [createFile,createImage]

firstMessage = """

I want that you create a prompt of any image that you want in preference add some randomness, and using that prompt to create a image and save it,
also create a .txt where you save that prompt.

"""

name1 ,name2, profession1, profession2 =  'Juan','Sebas','teacher','police'

sys_msgGPT4 = f"You are {name1}, you are {profession1}"
sys_msgGPT4 = SystemMessage(content = sys_msgGPT4)

numImages = 2

gpt4_1_chat = ChatOpenAI(model="gpt-4o", temperature=0)
gpt4_1_chat = gpt4_1_chat.bind_tools(listTool)

class State(MessagesState):
  count: int

# --------

def callingGPT4(state: State) -> dict:
    loop_inst = HumanMessage(
        content=firstMessage
    )
    ctx = [sys_msgGPT4] + state["messages"] + [loop_inst]
    numImages = 2
    resp: AIMessage = gpt4_1_chat.invoke(ctx)
    
    return {"messages": [resp],"count":state["count"]+1}

def route(state: State) -> Literal ["callingGPT4","__end__"]:

    return "__end__" if (state["count"] == numImages) else "callingGPT4"

# --------

builder = StateGraph(State)
builder.add_node("callingGPT4",callingGPT4)
builder.add_node("tools",ToolNode(listTool))

builder.add_edge(START, "callingGPT4")
#builder.add_edge("tools", "callingGPT4")

builder.add_conditional_edges(
"callingGPT4",
tools_condition,
{
    "tools":"tools",
    "__end__": END
})

builder.add_conditional_edges(
    "tools",
    route,
    {
        "callingGPT4": "callingGPT4",
        "__end__": END
    }
)
# -------

graph = builder.compile()
image = graph.get_graph().draw_mermaid_png()
with open("graphT.png", "wb") as f:
    f.write(image)

# -------

initial = {
    "messages":  [HumanMessage(content=firstMessage)],
    "count": 0
}

messages = graph.invoke(initial)
for m in messages['messages']:
    m.pretty_print()