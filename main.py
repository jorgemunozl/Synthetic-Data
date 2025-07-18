import asyncio
import os
from nodes import plannerNode, generatorNode, reflector
from nodes import evalSheetNode, image, router
from state import State
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from constants import directory


async def main(run_first_time: bool):
    thread_id = "session-1"
    builder = StateGraph(State)
    builder.add_node("planner", plannerNode)
    builder.add_node("generator", generatorNode)
    builder.add_node("reflector", reflector)
    builder.add_node("evalSheet", evalSheetNode)
    builder.add_node("router", router)
    builder.add_node("image", image)
    builder.add_edge(START, "planner")
    builder.add_edge("image", END)

    if run_first_time:
        initial_dict = {
            "messages": [],
            "seed": "",
            "number_generations": 0,
            "actual_number": 0,
            "plannerOutput": "",
            "generatorOutput": "",
            "difficultyIndex": 0,
            "topicIndex": 0,
            "evalSheet": "",
            "recursion": 0,
            "schemas_generations": [],
            "score": 0.0
        }
    else:
        async with AsyncSqliteSaver.from_conn_string(
            "checkpoint.sqlite"
        ) as saver:
            graph = builder.compile(checkpointer=saver)
            snapshot = await graph.aget_state(
                config={"configurable": {"thread_id": thread_id}}
            )
            initial_dict = dict(snapshot.values)

    initial = State(**initial_dict)

    async with AsyncSqliteSaver.from_conn_string("checkpoint.sqlite") as saver:
        graph = builder.compile(checkpointer=saver)
        result = await graph.ainvoke(  
            initial, config={"configurable": {"thread_id": thread_id}}
        )
        """
        snapshot = await graph.aget_state(
            config={"configurable": {"thread_id": thread_id}}
        )
        latest_state = snapshot.values
        os.makedirs(directory, exist_ok=True)
        for flow in latest_state["schemas_generations"]:
            name = directory + flow["id"] + ".md"
            print(f" -> Writing : {name}")
            with open(name, "w") as f:
                f.write(flow["content"])
                """
if __name__ == "__main__":
    asyncio.run(main(True))
