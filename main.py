def main():
    
    initial = {
        "messages":  [HumanMessage(content=firstMessage)],
        "count": 0
    }

    messages = graph.invoke(initial)
    for m in messages['messages']:
        m.pretty_print()

if __name__ == "__main__":
    main()
