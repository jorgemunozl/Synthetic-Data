from pydantic import BaseModel, Field
from typing import Optional
from models import NodesVariant, EdgesVariant

directoryOutput = "outputModel"

NUM_IMAGES_TO_ADD = 1


NODE = [
  {"id": "n1", "type": "start", "label": "Inicio"},
  {"id": "n2", "type": "decision", "label": "¿Quieres café?"},
  {"id": "n3", "type": "decision", "label": "¿Hay café?"},
  {"id": "n4", "type": "task", "label": "Hacer café"},
  {"id": "n5", "type": "task", "label": "Calentar café"},
  {"id": "n6", "type": "task", "label": "Servir en taza"},
  {"id": "n7", "type": "decision", "label": "¿Dulce OK?"},
  {"id": "n8", "type": "task", "label": "Añadir azúcar"},
  {"id": "n9", "type": "task", "label": "Tomar café"},
  {"id": "n10", "type": "end", "label": "Fin"}
]

EDGE = [
  {"id": "e1", "from": "n1", "to": "n2", "condition": None},
  {"id": "e2", "from": "n2", "to": "n10", "condition": "no"},
  {"id": "e3", "from": "n2", "to": "n3", "condition": "yes"},
  {"id": "e4", "from": "n3", "to": "n5", "condition": "yes"},
  {"id": "e5", "from": "n3", "to": "n4", "condition": "no"},
  {"id": "e6", "from": "n4", "to": "n6", "condition": None},
  {"id": "e7", "from": "n5", "to": "n6", "condition": None},
  {"id": "e8", "from": "n6", "to": "n7", "condition": None},
  {"id": "e9", "from": "n7", "to": "n9", "condition": "yes"},
  {"id": "e10", "from": "n7", "to": "n8", "condition": "no"},
  {"id": "e11", "from": "n8", "to": "n7", "condition": None},
  {"id": "e12", "from": "n9", "to": "n10", "condition": None}
]


class SeedBase(BaseModel):
    name: str = Field(default="process_coffee",
                      description="Name of the flowchart")
    descript: str = Field(default="Process to prepare and drink coffee",
                          description="Description of the flowchart")
    startNode: Optional[str] = Field(default="n1",
                                     description="Where the flowchart begins")
    nodes: list[NodesVariant] = Field(default_factory=lambda: NODE,
                                      description="List of nodes")
    edges: list[EdgesVariant] = Field(default_factory=lambda: EDGE,
                                      description="List of Edges")
