from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing_extensions import Literal
from models import GeneratorVariantOutput
from state import State
from prompts import promptSystem, promptHuman, promptImage
from prompts import promptTopicHum, promptTopicSys, promptValidator
from openai import OpenAI
import os
from constants import directoryOutput, NUM_IMAGES_TO_ADD
from config import GraphConfig
from langgraph.types import Command
import base64
import uuid
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import numpy as np



def create_file(path):
    client = OpenAI()
    with open(path, "rb") as f:
        response = client.files.create(file=f, purpose="vision")
    return response.id

def parse_score_and_text(response: str):
    pattern = r'^\s*(0(?:\.\d+)?|1(?:\.0+)?)\s+(.*)$'
    m = re.match(pattern, response.strip())
    if not m:
        raise ValueError("Response doesn't match the expected format")
    score = float(m.group(1))
    text = m.group(2).strip()
    return score, text

async def generateTopic(state: State) -> Command[Literal["generateVariants"]]:
    llmTopic = ChatOpenAI(model=GraphConfig().base,
                          temperature=GraphConfig().model_temperature)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptTopicSys),
        ("human", promptTopicHum)
    ])
    chain = prompt | llmTopic
    response = await chain.ainvoke({})
    return Command(update={"topic": response.content}, goto="generateVariants")


async def generateVariants(state: State) -> Command[Literal["createImage"]]:
    llm = ChatOpenAI(model=GraphConfig().base,
                     temperature=GraphConfig().model_temperature)
    llm = llm.with_structured_output(GeneratorVariantOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", promptSystem),
        ("human", promptHuman)
    ])
    chain = prompt | llm
    response = await chain.ainvoke(
        {"seed_value": state.seed, "topic": state.topic}
    )
    print(f""" -> Creating the schema number {state.number_generations}
    with topic : {state.topic}""")
    response = GeneratorVariantOutput.model_validate(response)
    output_model: GeneratorVariantOutput = response
    my_dict = output_model.model_dump()
    my_id = str(uuid.uuid4())
    my_dict["id"] = my_id
    print(my_dict)
    updated = list(state.schemas_generations)
    updated.append(my_dict)
    print(f" -> Schema number {state.number_generations} created!")
    #print(updated)
    return Command(update={"schemas_generations": updated}, goto="createImage")


def createImage(state: State) -> Command[Literal["generateTopic", "validator"]]:
    variant = state.schemas_generations[state.number_generations]    
    id = variant["id"]
    print(f" -> Creating the image number --{state.number_generations}-- about --{state.topic}--")
    dir_path = directoryOutput
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{id}.png")
    plot(variant,file_path)
    plot(variant, "flow.png")
    print(f" -> Image with: {id} created")
    return Command(update={"number_generations": state.number_generations+1,
                          "pathToImage":file_path,"actualRecursion":0},
                   goto="validator")


def validator(state: State) -> Command[Literal["tweaker", "generateTopic","__end__"]]:
    with open(state.pathToImage, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    uri = f"data:image/png;base64,{b64}"
    variant = state.schemas_generations[state.number_generations-1]
    client = OpenAI()
    print(f" -> Watching flowchart about --{state.topic}--")
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": promptValidator(variant,state.threshold)},
                    {
                        "type": "input_image",
                        "image_url": uri,
                    },
                ],
            },
        ],
    )
    reply = response.output_text
    score, prompt = parse_score_and_text(reply)
    print(f"SCORE -> {score}")
    print(f"FEEDBACK -> {prompt}")
    stoptIteration = state.actual_number + NUM_IMAGES_TO_ADD
    if (score >= state.threshold and state.number_generations < stoptIteration):
        goto = "generateTopic"  
    if (score <= state.threshold and state.actualRecursion != state.recursionLimit):
        goto = "tweaker"
    else:
        goto = "__end__"
    print(" -> Modified Numbers : ", state.actualRecursion)
    print(f" -> Going to  : {goto}")
    return Command(update={"modification": prompt}, goto=goto)


def tweaker(state: State) -> Command[Literal["validator"]]:
    client = OpenAI()
    print(" -> Creating modified image ")
    result = client.images.edit(
    quality="high",
    model="gpt-image-1",
    image=[
        open(state.pathToImage, "rb")
    ],
    prompt=state.modification
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    with open(state.pathToImage, "wb") as f:
        f.write(image_bytes)
    print(" -> Image modified created returning to validator")
    return Command(update={"actualRecursion":state.actualRecursion+2},goto="validator")


def calc_point(node, side):
    x, y, w, h = node['x'], node['y'], node['width'], node['height']
    
    if node['type'] == 'decision':
        if side == 'top': return (x, y + h/2)
        if side == 'bottom': return (x, y - h/2)
        if side == 'left': return (x - w/2, y)
        if side == 'right': return (x + w/2, y)
    elif node['type'] == 'end' or node['type'] == 'start' :
        radius = min(w, h) / 2
        angle = {'top': np.pi/2, 'bottom': -np.pi/2, 
                 'left': np.pi, 'right': 0}[side]
        return (x + radius * np.cos(angle), y + radius * np.sin(angle))
    else:
        if side == 'top': return (x, y + h/2)
        if side == 'bottom': return (x, y - h/2)
        if side == 'left': return (x - w/2, y)
        if side == 'right': return (x + w/2, y)


def plot(dicta,filename):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect('equal')
    ax.axis('off')

    node_map = {node['id']: node for node in dicta['nodes']}

    for node in dicta['nodes']:
        x, y, w, h = node['x'], node['y'], node['width'], node['height']
        text = node['text']
        
        if node['type'] == 'decision':
            points = [
                (x, y + h/2), (x + w/2, y),
                (x, y - h/2), (x - w/2, y)
            ]
            patch = patches.Polygon(points, closed=True, 
                                edgecolor='black', facecolor='white', 
                                linewidth=1)
        elif node['type'] == 'end' or node['type'] == 'start' :
            radius = min(w, h) / 2
            patch = patches.Circle((x, y), radius,
                                edgecolor='black', facecolor='white',
                                linewidth=1)
        else:
            patch = patches.Rectangle((x - w/2, y - h/2), w, h,
                                    edgecolor='black', facecolor='white',
                                    linewidth=1)
        
        ax.add_patch(patch)
        ax.text(x, y, text, ha='center', va='center', fontsize=10)
    for edge in dicta['edges']:   
        from_node = node_map[edge['from_']] 
        to_node = node_map[edge['to']]
    
        start = calc_point(from_node, edge['fromSide'])
        end = calc_point(to_node, edge['toSide'])
    
        arrow = FancyArrowPatch(start, end, 
                           arrowstyle='->', 
                           mutation_scale=10,
                           linewidth=1,
                           color='black')
        ax.add_patch(arrow)
        if 'label' in edge:
            label_x = (start[0] + end[0]) / 2
            label_y = (start[1] + end[1]) / 2
            ax.text(label_x, label_y, edge['label'], 
               ha='center', va='center', fontsize=9,
               bbox=dict(facecolor='white', alpha=1, edgecolor='none', pad=2))
    all_x = [node['x'] for node in dicta['nodes']]
    all_y = [node['y'] for node in dicta['nodes']]
    x_padding = 70
    y_padding = 25
    
    ax.set_xlim(min(all_x) - x_padding, max(all_x) + x_padding)
    ax.set_ylim(min(all_y) - y_padding, max(all_y) + y_padding)
    plt.savefig(filename, dpi=300, bbox_inches='tight')