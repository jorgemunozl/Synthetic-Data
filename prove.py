import json
from nodes import plot

with open("outputModel/schemas_generations.json", "r") as f:
    data = json.load(f)  # data is a list of dicts
first_dict = data[0]

plot(data[6],"eso.png")