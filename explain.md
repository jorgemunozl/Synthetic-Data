# Primitives
## a. Langchain
### 1. prompt: 
String template con variables, basado en formato ninja => prompt1: "mi nombre es {name}" => prompt1.name = joel => prompt1 = "mi nombre es joel"

### 2. output_parsers => 
structured output => "oye analiza si el comprador esta molesto o feliz, pero respondeme de la siguiente forma '{response: "feliz"}'" => "{response: triste}"

### 3. llm:
packages ya listos de los models para consumirlos => axios.post ("https://api.openai.com/")

### 4. chain (runnable):
llm (tools) + output_parser + prompt

### 5. Tools:
function calling => brinda las definiciones => una tool es una function que lo que hace es decirle al modelo que datos ingresa y que datos exactos quiere que retorne,


### 6. Runnable:
Multifunctional cognitive o non cognitive process


# Langgraph
1. States:
Bitacora, que permite al LLM tener un contexto continuo de lo que hace o de lo que esta pasando

2. Graphs(agent):
Orchestrator, definen el comportamiento de una aplicacion cognitva ( nodes + edges + states)

3. Nodes:
Funciones que encapsulan las acciones de las instancias

4. Edges:
Aristas

5. Store
memoria a largo plazo