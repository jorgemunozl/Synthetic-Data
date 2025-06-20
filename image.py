import os
import requests
from openai import OpenAI





prompt_mine1= """A flowchart empty"""

"""
"nodes": [
    { "id": "n1", "type": "start", "label": "Inicio" },
    { "id": "n2", "type": "decision", "label": "¿Quieres café?" },
    { "id": "n3", "type": "decision", "label": "¿Hay café?" },
    { "id": "n4", "type": "task", "label": "Hacer café" },
  ],
  "edges": [
    { "id": "e1", "from": "n1", "to": "n2", "condition": null },
    { "id": "e2", "from": "n2", "to": "n10", "condition": "NO" },
    { "id": "e3", "from": "n2", "to": "n3", "condition": "SI" },
    { "id": "e4", "from": "n3", "to": "n5", "condition": "SI" },
    { "id": "e5", "from": "n3", "to": "n4", "condition": "NO" },
  ]
"""



