from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from state import State, ReflectionOutput
from prompts import planner, generator, reflection, evalSheet
from config import GraphConfig
from langgraph.types import Command
import uuid
from constants import directoryMD, directoryPNG, directoryMer, difficulty
import subprocess
import re


def extract_mermaid_from_markdown(md_content):
    pattern = r'```mermaid\s*([\s\S]*?)```'
    matches = re.findall(pattern, md_content)
    if matches:
        return matches[0].strip()
    else:
        return ""


def convert_mmd_to_png(input_file, output_file):
    cmd = [
        'curl',
        '-X', 'POST',
        'https://kroki.io/mermaid/png',
        '-H', 'Content-Type: text/plain',
        '--data-binary', f'@{input_file}',
        '-o', output_file
    ]
    subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )


def print_state(state: State, node_name: str):
    print(f"\n----- {node_name.upper()} -----")
    print("--- STATES ---")
    for k, v in vars(state).items():
        if k in ("plannerOutput", "evalSheet", "generatorOutput"):
            val = str(v)[:20] + ("..." if v and len(str(v)) > 20 else "")
            print(f"  {k}: {val}")
        elif k == "schemas_generations":
            continue
        else:
            print(f"  {k}: {v}")
    print("--- END STATES ---\n")


async def plannerNode(state: State) -> Command[Literal["evalSheet"]]:
    print_state(state, "PLANNER")
    llm = ChatOpenAI(model=GraphConfig().modelBase,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", planner.System),
        ("human", planner.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({
        "difficulty": difficulty[state.difficultyIndex],
        "topic": state.promptUser
    })
    print(f"--- PLANNER OUTPUT ---\n{response.content}")
    return Command(update={"plannerOutput": response.content, "recursion": 0},
                   goto="evalSheet")


async def evalSheetNode(state: State) -> Command[Literal["generator"]]:
    print_state(state, "EVALSHEET")
    llm = ChatOpenAI(model=GraphConfig().modelBase,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", evalSheet.System),
        ("human", evalSheet.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"prompt": state.plannerOutput})
    print(f"--- EVALSHEET OUTPUT ---\n{response.content}")
    return Command(update={"evalSheet": response.content}, goto="generator")


async def generatorNode(state: State) -> Command[Literal["reflector"]]:
    print_state(state, "GENERATOR")
    llm = ChatOpenAI(model=GraphConfig().modelBase,
                     temperature=GraphConfig().temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", generator.System),
        ("human", generator.Human)
    ])
    chain = prompt | llm
    response = await chain.ainvoke({"indications": state.plannerOutput})
    print(f"--- GENERATOR OUTPUT ---\n{response.content}")
    return Command(update={"generatorOutput": response.content},
                   goto="reflector")


async def reflector(state: State) -> Command[Literal["generator", "router"]]:
    print_state(state, "REFLECTOR")
    llm = ChatOpenAI(
        model=GraphConfig().modelReasoning
    ).with_structured_output(ReflectionOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", reflection.System),
        ("human", reflection.Human)
    ])
    chain = prompt | llm
    result = await chain.ainvoke({
        "sheet": state.evalSheet,
        "target": state.generatorOutput
    })

    if isinstance(result, dict):
        score = result.get('score', 0.0)
        feedback = result.get('feedback', "No feedback provided.")
    else:
        score = getattr(result, 'score', 0.0)
        feedback = getattr(result, 'feedback', "No feedback provided.")

    print(f"--- REFLECTOR SCORE: {score}, FEEDBACK: ---\n{feedback}")
    if (
        score < GraphConfig().threshold
        and state.recursion < GraphConfig().recursionLimit
    ):
        feedback = state.generatorOutput + " -> Modifications" + feedback
        update = {"plannerOutput": feedback, "recursion": state.recursion+1}
        goto = "generator"
    else:
        newSchemas = list(state.schemas_generations)
        variant = {"id": str(uuid.uuid4()), "content": state.generatorOutput}
        newSchemas.append(variant)
        update = {"schemas_generations": newSchemas,
                  "actual_number": state.actual_number+1}
        goto = "router"
    return Command(update=update, goto=goto)


async def router(state: State) -> Command[Literal["planner", "image"]]:
    print_state(state, "ROUTER")
    max = state.diffUser*3
    update = {}
    if (state.actual_number == max):
        goto = "image"
    else:
        step = state.diffUser
        if (state.actual_number % step == step-1):
            update["difficultyIndex"] = (state.difficultyIndex+1) % 3
        goto = "planner"
    print(f"--- ROUTER UPDATE: {update}, GOTO: {goto} ---")
    return Command(update=update, goto=goto)


async def image(state: State) -> Command[Literal["__end__"]]:
    print_state(state, "IMAGE")
    update = {"imagesGenerated": [], "mermaidGenerated": []}
    for flowchart in state.schemas_generations:
        md_name = directoryMD + flowchart["id"] + ".md"
        with open(md_name, "w") as f:
            f.write(flowchart["content"])
        mmd_name = directoryMer + flowchart["id"] + ".mmd"
        extracted_content = extract_mermaid_from_markdown(flowchart["content"])
        update["mermaidGenerated"].append(extracted_content)
        with open(mmd_name, "w") as f:
            f.write(extracted_content)
        png_name = directoryPNG + flowchart["id"] + ".png"
        convert_mmd_to_png(mmd_name, png_name)
        update["imagesGenerated"].append(png_name)
        print(f" -> Converted {mmd_name} to {png_name}")

    print("--- IMAGE: All schemas exported. ---")
    return Command(update=update, goto="__end__")
