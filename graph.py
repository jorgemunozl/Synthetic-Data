from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.types import Command
from langgraph.prebuilt import ToolNode, tools_condition

from openai import OpenAI

import os, getpass
import json
import requests
from typing_extensions import Literal

from nodes import *
from config import GraphConfig

listTool = [createFile,createImage]

#builder = StateGraph(State, config=GraphConfig)
builder = StateGraph(State)

builder.add_node("generate_variants",generate_variants)

builder.add_edge(START, "generate_variants")
builder.add_edge("generate_variants",END)

graph = builder.compile()
image = graph.get_graph().draw_mermaid_png()
with open("graphT.png", "wb") as f:
    f.write(image)

# builder.add_node("tools",ToolNode(listTool))
#gpt4_1_chat = gpt4_1_chat.bind_tools(listTool)
#builder = StateGraph(State, config=GraphConfig)

"""
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

"""
# -------


# sys_msgGPT4 = f"You are {skill0} and {skill1}"
# skill0 , skill1 = "creative", "tidy"
# sys_msgGPT4 = SystemMessage(content = sys_msgGPT4)