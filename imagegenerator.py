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


# Let's create a bucle


def createImage(prompt: str, name: str, size: str = "1024x1024", quality: str = "standard") -> bool:
    """
    Create an image and save it as .png

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
        with open(name, 'wb') as f:
            f.write(img_data)
        return True
    except Exception as e:
        print(f"Error creating image: {e}")
        return False

def createFile(text: str, namefile:str) -> None:
    """
    Saves a string as a .txt

    Args:
        text: str
        namefile: str 
    """
    with open(namefile,"w") as f:
        f.write(text)
    return None

listTool = [createFile,createImage]

firstMessage = """

I want that you create a prompt for family in the beach, and using that prompt create a image and save it,
also create a .txt saying that you succed if that were the case

"""

name1 ,name2, profession1, profession2 =  'Juan','Sebas','teacher','police'

sys_msgGPT4 = f"You are {name1}, you are {profession1}"
sys_msgGPT4 = SystemMessage(content = sys_msgGPT4)

numImages = 2

gpt4_1_chat = ChatOpenAI(model="gpt-4o", temperature=0)
gpt35_chat = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
gpt4_1_chat = gpt4_1_chat.bind_tools(listTool)

class State(MessagesState):
  count: int

# --------

def callingGPT4(state: State) -> dict:
  resp: AIMessage = gpt4_1_chat.invoke([sys_msgGPT4]+state["messages"])
  return {"messages": [resp],"count":state["count"]+1}
# --------

builder = StateGraph(State)
builder.add_node("callingGPT4",callingGPT4)
builder.add_node("createFile",ToolNode(listTool))

builder.add_edge(START, "callingGPT4")
builder.add_edge("createFile", "callingGPT4")

#builder.add_edge("callingGPT4",route)

builder.add_conditional_edges(
"callingGPT4",
tools_condition,
{
    "tools":"createFile",
})

builder.add_edge("createFile","callingGPT4")
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