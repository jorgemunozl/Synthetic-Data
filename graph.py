from langgraph.graph import StateGraph, START, END
from langchain_core.runnables.graph import MermaidDrawMethod
import json
from nodes import generate_variants, createImage, route
from state import State
from constants import NUM_IMAGE_WE_HAVE

builder = StateGraph(State)
builder.add_node("generate_variants", generate_variants)
builder.add_node("createImage", createImage)

builder.add_edge(START, "generate_variants")
builder.add_edge("generate_variants", "createImage")

builder.add_conditional_edges(
   "createImage",
    route,
    {
        "generate_variants": "generate_variants",
        "__end__": END,
    },
)

graph = builder.compile()
image = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
with open("outputModel/graphLanggraph.png", "wb") as f:
    f.write(image)

initial = {
    "messages": [],
    "seed": "",
    "number_generations": NUM_IMAGE_WE_HAVE + 1,
    "schemas_generations": []
    }

result = graph.ainvoke(initial)

print(result)

#with open("numImage.json", "r") as f:
 #   dataNum = json.load(f)

# dataNum["numImages"] = result["number_generations"] - 1

#with open("numImage.json", "w") as f:
 #   json.dump(dataNum, f)

# print("SUCCESS")
