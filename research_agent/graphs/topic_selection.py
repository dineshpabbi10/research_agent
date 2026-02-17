import asyncio
from langgraph.types import interrupt
from langgraph.graph import StateGraph,START,END

from research_agent.models.topic_selection import TopicSelectionState
from research_agent.nodes.topic_selection import check_human_feedback, check_topic_broadness, get_human_feedback
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

checkpointer = InMemorySaver()

topic_selection_graph = StateGraph(TopicSelectionState)

topic_selection_graph.add_node("check_human_feedback", check_human_feedback)
topic_selection_graph.add_node("check_topic_broadness", check_topic_broadness)
topic_selection_graph.add_node("get_human_feedback", get_human_feedback)

topic_selection_graph.add_edge(START, "check_human_feedback")
topic_selection_graph.add_edge("check_human_feedback", "check_topic_broadness")
topic_selection_graph.add_edge("check_topic_broadness", "get_human_feedback")
topic_selection_graph.add_edge("get_human_feedback", END)

compiled_topic_selection_graph = topic_selection_graph.compile(checkpointer=checkpointer)
