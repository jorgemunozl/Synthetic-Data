from pydantic import BaseModel, Field
from typing import Optional
from models import NodesVariant, EdgesVariant

directoryOutput = "outputModel"

NUM_IMAGES_TO_ADD = 1

nodes = [
        {"id": "n1", "type": "start", "text": "Start", "x": 200, "y": 1600, "width": 18000, "height": 300},
        {"id": "n2", "type": "task", "text": "Identify Business Needs", "x": 200, "y": 1250, "width": 820, "height": 150},
        {"id": "n3", "type": "task", "text": "Research Software Options", "x": 200, "y": 1000, "width": 820, "height": 150},
        {"id": "n4", "type": "task", "text": "Evaluate and Select Software", "x": 200, "y": 750, "width": 820, "height": 150},
        {"id": "n5", "type": "decision", "text": "Is the Selected \n Software Approved?", "x": 200, "y": 300, "width": 820, "height": 370},
        {"id": "n6", "type": "task", "text": "Gain Approval from \n Stakeholders", "x": -1000, "y": 300, "width": 420, "height": 250},
        {"id": "n7", "type": "task", "text": "Design Implementation \n Plan", "x": 200, "y": -300, "width": 820, "height": 250},
        {"id": "n8", "type": "task", "text": "Setup and Configuration", "x": 200, "y": -700, "width": 720, "height": 150},
        {"id": "n9", "type": "task", "text": "Test the System", "x": 200, "y": -1000, "width": 480, "height": 250},
        {"id": "n10", "type": "decision", "text": "Does the System \n Pass Testing?", "x": 200, "y": -1500, "width": 720, "height": 470},
        {"id": "n11", "type": "task", "text": "Conduct Training", "x": 200, "y": -2000, "width": 880, "height": 250},
        {"id": "n12", "type": "task", "text": "Deploy \n System", "x": -900, "y": -2000, "width":480, "height": 250},
        {"id": "n13", "type": "task", "text": "Monitor and \n Support", "x": -900, "y": -1500, "width": 780, "height": 250},
        {"id": "n14", "type": "end", "text": "Implementation \n Complete", "x": -900, "y": -900, "width": 42330, "height": 580}
        ],
edges = [
        {"id": "e1", "from_": "n1", "to": "n2", "fromSide": "bottom", "toSide": "top"},
        {"id": "e2", "from_": "n2", "to": "n3", "fromSide": "bottom", "toSide": "top"},
        {"id": "e3", "from_": "n3", "to": "n4", "fromSide": "bottom", "toSide": "top"},
        {"id": "e4", "from_": "n4", "to": "n5", "fromSide": "bottom", "toSide": "top"},
        {"id": "e5", "from_": "n5", "to": "n6", "label": "NO", "fromSide": "left", "toSide": "right"},
        {"id": "e6", "from_": "n6", "to": "n5", "fromSide": "right", "toSide": "left"},
        {"id": "e7", "from_": "n5", "to": "n7", "label": "YES", "fromSide": "bottom", "toSide": "top"},
        {"id": "e8", "from_": "n7", "to": "n8", "fromSide": "bottom", "toSide": "top"},
        {"id": "e9", "from_": "n8", "to": "n9", "fromSide": "bottom", "toSide": "top"},
        {"id": "e10", "from_": "n9", "to": "n10", "fromSide": "bottom", "toSide": "top"},
        {"id": "e11", "from_": "n10", "to": "n11", "label": "YES", "fromSide": "bottom", "toSide": "top"},
        {"id": "e12", "from_": "n11", "to": "n12", "fromSide": "left", "toSide": "right"},
        {"id": "e13", "from_": "n12", "to": "n13", "fromSide": "top", "toSide": "bottom"},
        {"id": "e14", "from_": "n13", "to": "n14", "fromSide": "top", "toSide": "bottom"},
        {"id": "e15", "from_": "n10", "to": "n8", "label": "NO", "fromSide": "left", "toSide": "left"}
    ]


class SeedBase(BaseModel):
    name: str = Field(default="process_coffee",
                      description="Name of the flowchart")
    descript: str = Field(default="Process to prepare and drink coffee",
                          description="Description of the flowchart")
    startNode: Optional[str] = Field(default="n1",
                                     description="Where the flowchart begins")
    nodes: list[NodesVariant] = Field(default_factory=lambda: nodes,
                                      description="List of nodes")
    edges: list[EdgesVariant] = Field(default_factory=lambda: edges,
                                      description="List of Edges")
