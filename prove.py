import mermaid as md
from mermaid.graph import Graph

render = md.Mermaid("""
stateDiagram-v2
    [*] --> Still
    Still --> [*]

    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
""")
