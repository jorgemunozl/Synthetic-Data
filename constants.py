from pydantic import BaseModel, Field
from typing import Optional
from models import NodesVariant
import json


class SeedBase(BaseModel):
  name: str = Field(default = "process_coffee", description = "something")
  description: str = Field(default = "Process to prepare and drink coffee")
  startNode: Optional[str]      = Field(description = "")
  nodes: Optional[NodesVariant] = Field(description = "")
  edges: Optional[str]          = Field(description = "")


"""
  "description": ",
  "version": "1.0",
  "startNode": "n1",
  "nodes": [
    { "id": "n1", "type": "start", "label": "Inicio" },
    { "id": "n2", "type": "decision", "label": "¿Quieres café?" },
    { "id": "n3", "type": "decision", "label": "¿Hay café?" },
    { "id": "n4", "type": "task", "label": "Hacer café" },
    { "id": "n5", "type": "task", "label": "Calentar café" },
    { "id": "n6", "type": "task", "label": "Servir en taza" },
    { "id": "n7", "type": "decision", "label": "¿Dulce OK?" },
    { "id": "n8", "type": "task", "label": "Añadir azúcar" },
    { "id": "n9", "type": "task", "label": "Tomar café" },
    { "id": "n10", "type": "end", "label": "Fin" }
  ],
  "edges": [
    { "id": "e1", "from": "n1", "to": "n2", "condition": null },
    { "id": "e2", "from": "n2", "to": "n10", "condition": "NO" },
    { "id": "e3", "from": "n2", "to": "n3", "condition": "SI" },
    { "id": "e4", "from": "n3", "to": "n5", "condition": "SI" },
    { "id": "e5", "from": "n3", "to": "n4", "condition": "NO" },
    { "id": "e6", "from": "n4", "to": "n6", "condition": null },
    { "id": "e7", "from": "n5", "to": "n6", "condition": null },
    { "id": "e8", "from": "n6", "to": "n7", "condition": null },
    { "id": "e9", "from": "n7", "to": "n9", "condition": "SI" },
    { "id": "e10", "from": "n7", "to": "n8", "condition": "NO" },
    { "id": "e11", "from": "n8", "to": "n7", "condition": null },
    { "id": "e12", "from": "n9", "to": "n10", "condition": null }
  ]
"""