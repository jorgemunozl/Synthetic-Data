import os, getpass
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command
from typing_extensions import Literal
from langgraph.prebuilt import ToolNode, tools_condition

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

# prompt => string template con variables, basado en formato ninja => prompt1: "mi nombre es {name}" => prompt1.name = joel => prompt1 = "mi nombre es joel"
# output_parsers => structured output => "oye analiza si el comprador esta molesto o feliz, pero respondeme de la siguiente forma '{response: "feliz"}'" => "{response: triste}"
# llm => packages ya listos de los models para consumirlos => axios.post ("https://api.openai.com/")
# chain (runnable) => llm + output parser. + prompt =>
# tools => function calling => brinda las definiciones => una tool es una function que lo que hace es decirle al modelo que datos ingresa y que datos exactos quiere que retorne,

firstMessage = 'I want that you put "im gonna to love Elon Musk" in a file .txt called Elon'
name1 ,name2, profession1, profession2 =  'Juan','Sebas','teacher','police'
sys_msgGPT4 = f"You are {name1}, you are {profession1}"
sys_msgGPT3 = f"You are {name2}, you are {profession2}"


sys_msgGPT4 = SystemMessage(content = sys_msgGPT4)
sys_msgGPT3 = SystemMessage(content = sys_msgGPT3)

interaction = 2

gpt4_1_chat = ChatOpenAI(model="gpt-4o", temperature=0)
gpt35_chat = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

gpt4_1_chat = gpt4_1_chat.bind_tools([createFile])
gpt35_chat = gpt35_chat.bind_tools([createFile])

class State(MessagesState):
  count: int

# --------

def callingGPT4(state: State) -> dict:
  resp: AIMessage = gpt4_1_chat.invoke([sys_msgGPT4]+state["messages"])
  return {"messages": [resp],"count":state["count"]+1}

def callingGPT35(state: State) -> dict:
    resp: AIMessage = gpt35_chat.invoke([sys_msgGPT3]+state["messages"]) 
    return {"messages": [resp],"count":state["count"]+1}

def route4(state: State) -> Literal["callingGPT35", "__end__"]:
    return "__end__" if (state["count"] >= interaction) else "callingGPT35"

def route35(state: State) -> Literal["callingGPT4", "__end__"]:
    return "__end__" if (state["count"] >= interaction) else "callingGPT4"

# --------

builder = StateGraph(State)
builder.add_node("callingGPT4",callingGPT4)
builder.add_node("createFile",ToolNode([createFile]))

builder.add_edge(START, "callingGPT4")
builder.add_edge("createFile", "callingGPT4")
builder.add_conditional_edges(
"callingGPT4",
tools_condition,
{
    "tools":"createFile",
    "__end__":END
}
)

#builder.add_conditional_edges("callingGPT4", route4, {"createFile":"createFile","__end__":END})#"callingGPT35": "callingGPT35", "__end__": END})
#builder.add_conditional_edges("callingGPT35", route35, {"createFile":"createFile","callingGPT4": "callingGPT4", "__end__": END})

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


#   builder.add_node(callingGPT35,callingGPT35)
