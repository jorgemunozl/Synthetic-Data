from langgraph.graph import StateGraph, START, END
from nodes import generate_variants, createImage, route
from state import State


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
        })

