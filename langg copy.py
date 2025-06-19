import os, getpass
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command
from typing_extensions import Literal
from langgraph.prebuilt import ToolNode, tools_condition


# prompt => string template con variables, basado en formato ninja => prompt1: "mi nombre es {name}" => prompt1.name = joel => prompt1 = "mi nombre es joel"
# output_parsers => structured output => "oye analiza si el comprador esta molesto o feliz, pero respondeme de la siguiente forma '{response: "feliz"}'" => "{response: triste}"
# llm => packages ya listos de los models para consumirlos => axios.post ("https://api.openai.com/")
# chain (runnable) => llm + output parser. + prompt =>
# tools => function calling => brinda las definiciones => una tool es una function que lo que hace es decirle al modelo que datos ingresa y que datos exactos quiere que retorne,

gpt4_1_chat = ChatOpenAI(model="gpt-4o", temperature=0)
gpt35_chat = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

firstMessage = 'multiply 3*1234'
sys_msgGPT4 = "a"

sys_msgGPT4 = SystemMessage(content = sys_msgGPT4)

interaction = 2

def multiply(a:int, b:int) -> int:
    """Multiply a and b.

    Args: 
        a: first int
        b: second int
    """
    return a * b

gpt4Tool = gpt4_1_chat.bind_tools([multiply])

def tool_multiply(state: MessagesState):
    return {"messages":[gpt4Tool.invoke(state["messages"])]}


class State(MessagesState):
  count: int

# How I could that is ts

builder = StateGraph(MessagesState)
builder.add_node("tool_multiply",tool_multiply)
builder.add_node("tools",ToolNode([multiply]))

builder.add_edge(START,"tool_multiply")
builder.add_conditional_edges(
    "tool_multiply",
    tools_condition,
)
builder.add_edge("tools","tool_multiply")
graph = builder.compile()
image = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(image)

initial = {
    "messages":  [HumanMessage(content=firstMessage)],
}

messages = graph.invoke(initial)
print(messages)

for m in messages['messages']:
    m.pretty_print()