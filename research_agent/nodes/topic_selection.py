from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
from research_agent.models.topic_selection import (
    TopicSelectionState,
    TopicSelectionResult,
)
from research_agent.utils.config import ResearchAgentConfig
from research_agent.prompts.topic_selection import TOPIC_SELECTION_SYSTEM_PROMPT
from research_agent.utils.logger import setup_logger


logger = setup_logger(__name__)


async def check_human_feedback(state: TopicSelectionState) -> TopicSelectionState:
    """
    Check if the user has provided feedback on the suggested topic and update the state accordingly.
    """
    logger.info(state)
    if state.user_input is not None:
        state.selected_topic = (
            state.user_input if state.user_input != "accept" else state.suggested_topic
        )
    return state


async def check_topic_broadness(state: TopicSelectionState) -> TopicSelectionState:
    """
    Check if the given topic is broad or specific enough for a blog post.
    """
    if state.user_input is not None and state.user_input == "accept":
        logger.info(f"User accepted the suggested topic: {state.suggested_topic}")
        state.is_broad = False
        return state

    llm = ChatOpenAI(model=ResearchAgentConfig().model_name)
    llm = llm.with_structured_output(TopicSelectionResult)

    prompt = TOPIC_SELECTION_SYSTEM_PROMPT.format(user_topic=state.selected_topic)
    result = llm.invoke(prompt)
    # If topic is too broad, interrupt and ask user to select a more specific topic
    state.is_broad = result.is_broad
    state.suggested_topic = result.selected_topic
    return state


async def get_human_feedback(
    state: TopicSelectionState,
) -> Command | TopicSelectionState:
    """
    Get feedback from the user on whether they want to accept the suggested topic or not.
    """
    if state.is_broad and state.suggested_topic is not None:
        logger.info(
            f"Topic '{state.selected_topic}' is too broad. Suggested topic: '{state.suggested_topic}'"
        )
        user_input = interrupt(
            {
                "message": f"The topic '{state.selected_topic}' is too broad. Please select a more specific topic. I suggest the following topic: {state.suggested_topic}. Please type accept if you like the topic or provide your own topic",
                "type": "user_input_freetext",
            }
        )
        state.user_input = user_input
    elif state.is_broad:
        logger.info(
            f"Topic '{state.selected_topic}' is too broad and no suggested topic is available. Please provide a more specific topic."
        )
        user_input = interrupt(
            {
                "message": f"The topic '{state.selected_topic}' is too broad. Please select a more specific topic.",
                "type": "user_input_freetext",
            }
        )
        state.user_input = user_input
    elif state.is_broad == False:
        logger.info(
            f"Topic '{state.selected_topic}' is specific enough for a blog post."
        )
        return state

    logger.info("Rechecking the broadness of the topic based on user feedback.")
    return Command(goto="check_human_feedback", update={"user_input": state.user_input})
