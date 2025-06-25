from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from openai import OpenAI
import json
import requests
from typing_extensions import Literal
from nodes import *
from config import GraphConfig
from state import State

builder = StateGraph(State)

builder.add_node("generate_variants", generate_variants)
builder.add_node("tools",ToolNode([createImage]))

builder.add_edge(START, "generate_variants")
builder.add_conditional_edges(
    "generate_variants",
    tools_condition,
    {
        "tools":"tools",
        "__end__": END
    })
builder.add_conditional_edges(
    "tools",
    route,
    {
        "generate_variants": "generate_variants",
        "__end__": END
    }
)
#builder.add_edge("generate_variants",END)

graph = builder.compile()
#image = graph.get_graph().draw_mermaid_png()
#with open("graphT.png", "wb") as f:
#    f.write(image)

result = graph.invoke({
    "messages": [],
    "seed": "",
    "number_generations": 3,
    "schemas_generations": []
    })

output = result["schemas_generations"][0].model_dump()
output = GeneratorVariantOutput.model_validate(output)
output = output.model_dump_json(indent = 2)
print(output)

with open("seed.json", "w", encoding="utf-8") as f:
    f.write(output)








# MAIN PURPOSE OF THE GRAPH IS GENERATE THE BUCLE, IT RECIEVES A STRING IN JSON FORMATE AND USE THE TOOL, 
# CREATE IMAGE.
# I MEAN GENERATE VARIANTS FOR DEFAULT  

# Is generate variants create a json, and (for now) it simply return it. Now in what format is the problem.
# What recieves ??
# Save the list of Json (State.schemasgenerations) <- createFile
#builder = StateGraph(State, config_schema=GraphConfig) # What specifically make this?





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