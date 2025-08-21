import asyncio
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command


# Simple state with just a message and counter
class SimpleState(TypedDict):
    message: str
    counter: int


# Node 1: Initialize
async def start_node(state: SimpleState) -> Command[Literal["process"]]:
    print(f"🚀 START NODE: {state['message']}")
    return Command(
        update={"message": "Processing...", "counter": state["counter"] + 1},
        goto="process"
    )


# Node 2: Process
async def process_node(state: SimpleState) -> Command[Literal["finish"]]:
    print(f"⚡ PROCESS NODE: {state['message']}, Counter: {state['counter']}")
    return Command(
        update={"message": "Almost done!", "counter": state["counter"] + 1},
        goto="finish"
    )


# Node 3: Finish
async def finish_node(state: SimpleState) -> Command[Literal["__end__"]]:
    print(f"🎯 FINISH NODE: {state['message']}, Counter: {state['counter']}")
    return Command(
        update={"message": "Completed!", "counter": state["counter"] + 1},
        goto="__end__"
    )


async def run_simple_graph():
    # Build the graph
    builder = StateGraph(SimpleState)
    
    # Add nodes
    builder.add_node("start", start_node)
    builder.add_node("process", process_node)
    builder.add_node("finish", finish_node)
    
    # Add edges
    builder.add_edge(START, "start")
    builder.add_edge("finish", END)
    
    # Compile the graph
    graph = builder.compile()
    
    # Initial state
    initial_state = SimpleState(message="Hello Graph!", counter=0)
    
    print("=" * 50)
    print("🔥 STARTING MINIMAL LANGGRAPH TEST")
    print("=" * 50)
    
    # Run the graph
    result = await graph.ainvoke(initial_state)
    
    print("=" * 50)
    print("✅ GRAPH COMPLETED!")
    print(f"Final result: {result}")
    print("=" * 50)
    print(type(result))
    print(result["counter"])
    return result


if __name__ == "__main__":
    # Run the simple graph test
    result = asyncio.run(run_simple_graph())
