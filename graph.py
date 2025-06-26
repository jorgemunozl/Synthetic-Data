from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.runnables.graph import MermaidDrawMethod
import json
from typing_extensions import Literal
from nodes import *
from config import GraphConfig
from state import State

builder = StateGraph(State)
builder.add_node("generate_variants", generate_variants)
builder.add_node("createImage",createImage)
builder.add_edge(START, "generate_variants")
builder.add_edge("generate_variants","createImage")
builder.add_edge("createImage",END)

graph = builder.compile()

# image = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
# with open("graphLanggraph.png", "wb") as f:
#    f.write(image)

initial = {
    "messages": [],
    "seed": "",
    "number_generations": 0,
    "schemas_generations": []
    }

result = graph.invoke(initial)
print("SUCCESS")
