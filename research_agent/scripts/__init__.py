from research_agent.models.topic_selection import TopicSelectionState
from research_agent.graphs.topic_selection import compiled_topic_selection_graph
from langgraph.types import Command
import asyncio

async def test_graph():
    initial_state = TopicSelectionState(selected_topic=input("Enter a topic for your blog post: "))
    config = {"configurable":{"thread_id":"test_thread"}}
    command = None
    while True:
        if command is None:
            result = await compiled_topic_selection_graph.ainvoke(initial_state,config=config)
        else:
            result = await compiled_topic_selection_graph.ainvoke(command,config=config)
            command = None
        
        if("__interrupt__" in result and len(result["__interrupt__"]) > 0):
            interrupt_payload = result["__interrupt__"][0]
            if(interrupt_payload.value.get("type") == "user_input_freetext"):
                user_input = input(result["__interrupt__"][0].value['message'] +"\n")
                command = Command(resume=user_input)
        else:
            # No interrupt, graph completed successfully
            print(f"\nFinal topic selected: {result.get('selected_topic')}")
            print(f"Suggested topic: {result.get('suggested_topic')}")
            break


if __name__ == "__main__":
    asyncio.run(test_graph())