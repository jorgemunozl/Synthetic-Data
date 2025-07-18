from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from state import State
from prompts import planner, generator, reflection, evalSheet
from config import GraphConfig
from langgraph.types import Command
import uuid
import re
# import subprocess
from constants import directory

dif = ["easy", "medium", "hard"]


def parse_score_and_text(response: str):
    pattern = r'^\s*(.*?)\s+(0(?:\.\d+)?|1(?:\.0+)?)\s*$'
    m = re.match(pattern, response.strip())
    if not m:
        raise ValueError("Response doesn't match the expected format")
    text = m.group(1).strip()
    score = float(m.group(2))
    return score, text


async def plannerNode(state: State) -> Command[Literal["generator"]]:
    print("\n----- plannerNode -----")
    print("State:")
    for k, v in vars(state).items():
        print(f"  {k}: {v}")
    llm = ChatOpenAI(model=GraphConfig().modelBase,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", planner.System),
        ("human", planner.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"difficulty": dif[state.difficultyIndex],
                                    "topic": GraphConfig().topics[state.topicIndex]
                                    })
    print(f"[plannerNode] plannerOutput: {response.content}")
    return Command(update={"plannerOutput": response.content, "recursion": 0},
                   goto="generator")


async def evalSheetNode(state: State) -> Command[Literal["generator"]]:
    print("\n----- evalSheetNode -----")
    print("State:")
    for k, v in vars(state).items():
        print(f"  {k}: {v}")
    llm = ChatOpenAI(model=GraphConfig().modelBase,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", evalSheet.System),
        ("human", evalSheet.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"prompt": state.generatorOutput})
    print("-> Initial State: ", state)
    print(f"[evalSheetNode] evalSheet: {response.content}")
    return Command(update={"evalSheet": response.content}, goto="generator")


async def generatorNode(state: State) -> Command[Literal["reflector"]]:
    print("\n----- generatorNode -----")
    print("State:")
    for k, v in vars(state).items():
        print(f"  {k}: {v}")
    llm = ChatOpenAI(model=GraphConfig().modelBase,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", generator.System),
        ("human", generator.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"indications": state.plannerOutput})
    print(f"[generatorNode] generatorOutput: {response.content}")
    return Command(update={"generatorOutput": response.content},
                   goto="reflector")


async def reflector(state: State) -> Command[Literal["generator", "router"]]:
    print("\n----- reflector -----")
    print("State:")
    for k, v in vars(state).items():
        print(f"  {k}: {v}")
    llm = ChatOpenAI(model=GraphConfig().modelReasoning,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", reflection.System),
        ("human", reflection.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"sheet": state.evalSheet,
                                   "target": state.generatorOutput})
    score, feedback = parse_score_and_text(response.content)
    print(f"[reflector] score: {score}, feedback: {feedback}")
    if (score < GraphConfig().threshold and state.recursion < GraphConfig().recursionLimit):
        feedback = state.generatorOutput + "Modifications" + feedback
        update = {"plannerOutput": feedback, "recursion": state.recursion+1}
        goto = "generator"
    else:
        newSchemas = list(state.schemas_generations)
        variant = {"id": str(uuid.uuid4()), "content": state.generatorOutput}
        newSchemas = newSchemas.append(variant)
        update = {"schemas_generations":
                  newSchemas,
                  "actual_number": state.actual_number+1}
        goto = "router"
    print(f"[reflector] update: {update}, goto: {goto}")
    return Command(update=update, goto=goto)


async def router(state: State) -> Command[Literal["planner", "image"]]:
    print("\n----- router -----")
    print("State:")
    for k, v in vars(state).items():
        print(f"  {k}: {v}")
    max = GraphConfig().difficultyStep*len(GraphConfig().topics)*3
    if (state.actual_number == max-1):
        goto = "image"
    else:
        step = GraphConfig().difficultyStep
        if (state.actual_number % step == step-1):
            update = {"difficultyIndex": (state.difficultyIndex+1) % 3}
        elif (state.actual_number % (3*step-1) == 0):
            update = {"topicIndex": state.topicIndex + 1}
        goto = "planner"
    print(f"[router] update: {update}, goto: {goto}")
    return Command(update=update, goto=goto)


async def image(state: State) -> Command[Literal["__end__"]]:
    print("\n----- image -----")
    print("State:")
    for k, v in vars(state).items():
        print(f"  {k}: {v}")
    print(f"Exporting {len(state.schemas_generations)} schemas...")
    for flow in state.schemas_generations:
        name = directory+flow["id"]+".mmd"
        print(f"[image] Writing {name}")
        with open(name, "w") as f:
            f.write(flow["content"])
        # subprocess.run([
        #    "mmdc",
        #    "-i", name,
        #    "-o", name.replace(".mmd", ".png")
        # ], check=True)
        # curl -X POST https://kroki.io/mermaid/png -H
        #  "Content-Type: text/plain" -d 'graph TD; A-->B;' -o output.png
    print("[image] All schemas exported.")
    return Command(goto="__end__")
