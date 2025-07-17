from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from state import State
from prompts import planner, generator, reflection
from openai import OpenAI
from config import GraphConfig
from langgraph.types import Command
import base64
import uuid
import re
import subprocess
from constants import directory 


def parse_score_and_text(response: str):
    pattern = r'^\s*(0(?:\.\d+)?|1(?:\.0+)?)\s+(.*)$'
    m = re.match(pattern, response.strip())
    if not m:
        raise ValueError("Response doesn't match the expected format")
    score = float(m.group(1))
    text = m.group(2).strip()
    return score, text


async def plannerNode(state: State) -> Command[Literal["generator"]]:
    llmTopic = ChatOpenAI(model=GraphConfig().modelBase,
                          temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", planner.System),
        ("human", planner.Human)
    ])
    chain = prompt | llmTopic
    response = await chain.ainvoke({"difficulty": state.difficulty,
                                    "topic": state.topic})
    return Command(update={"plannerOutput": response.content,"recursion":0},
                   goto="generator")


async def generatorNode(state: State) -> Command[Literal["reflector"]]:
    llm = ChatOpenAI(model=GraphConfig().modelBase,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", generator.System),
        ("human", generator.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"indications": state.plannerOutput})
    # response = {"flowchart": response.content}
    # response["id"] = str(uuid.uuid4())
    # updated = (list(state.schemas_generations)).append(response)
    return Command(update={"generatorOutput": response.content},
                   goto="reflector")


async def reflector(state: State) -> Command[Literal["generator", "router"]]:
    llm = ChatOpenAI(model=GraphConfig().modelReasoning,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", reflection.System),
        ("human", generator.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"target": state.generatorOutput})
    score, feedback = parse_score_and_text(response.content)
    if (score < GraphConfig().threshold and state.recursion < GraphConfig().recursionLimit):
        update = {"plannerOutput": feedback, "recursion": state.recursion+1}
        goto = "generator"
    else:
        variant = {"id": str(uuid.uuid4()), "content": state.generatorOutput}
        update = {"schemas_generations":
                  state.schemas_generations.append(variant)}
        goto = "router"
    return Command(update=update, goto=goto)


async def router(state: State) -> Command[Literal["planner", "image"]]:
    max = GraphConfig().difficultyStep*len(GraphConfig().topics)*3
    if (state.actual_number == max):
        goto = "image"
    else:
        goto = "planner"
    return Command(goto=goto)


async def image(state: State) -> Command[Literal["__end__"]]:
    for flow in state.schemas_generations:
        name = directory+flow["id"]+".mmd"
        with open(name, "w") as f:
            f.write(flow["content"])
        subprocess.run([
            "mmdc",
            "-i", name,
            "-o", name.replace(".mmd", ".png")
        ], check=True)
        # Or curl -X POST https://kroki.io/mermaid/png -H
        #  "Content-Type: text/plain" -d 'graph TD; A-->B;' -o output.png
    return Command(goto="__end__")
