import os, getpass
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command
from typing_extensions import Literal
from langgraph.prebuilt import ToolNode, tools_condition
import requests
from openai import OpenAI
import json

from nodes import createFile

# from .config import GraphConfig

listTool = [createFile,createImage]


skill0 , skill1 = "creative", "tidy"

sys_msgGPT4 = f"You are {skill0} and {skill1}"
sys_msgGPT4 = SystemMessage(content = sys_msgGPT4)

numImages = 2

gpt4_1_chat = ChatOpenAI(model="gpt-4o", temperature=0)
gpt4_1_chat = gpt4_1_chat.bind_tools(listTool)


builder = StateGraph(State, config=GraphConfig)
builder.add_node("callingGPT4",callingGPT4)
builder.add_node("tools",ToolNode(listTool))

builder.add_edge(START, "callingGPT4")
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
