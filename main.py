def main():
    # -------

    initial = {
        "messages":  [HumanMessage(content=firstMessage)],
        "count": 0
    }

    # --------

    messages = graph.invoke(initial)
    for m in messages['messages']:
        m.pretty_print()


"""
{
  "flowId": "103944, int
  "name": "process_coffee", str
  "description": "Process to prepare and drink coffee", str
  "version": "1.0", 
  "startNode": "n1",
  "nodes": [
    { "id": "n1", "type": "start", "label": "Inicio" },
    { "id": "n2", "type": "decision", "label": "¿Quieres café?" },
  ],
  "edges": [ id=[(e1,n1,n2,condition)]
    { "id": "e1", "from": "n1", "to": "n2", "condition": null },
    { "id": "e2", "from": "n2", "to": "n10", "condition": "NO" },
  ]
}
"""







if __name__ == "__main__":
    main()
