from pydantic import BaseModel

class TopicSelectionState(BaseModel):
    """
    State for the topic selection phase of the research agent.
    """
    selected_topic: str 
    suggested_topic: str | None = None 
    user_input : str | None = None
    is_broad: bool | None = None

class TopicSelectionResult(BaseModel):
    """
    Result of the topic selection phase of the research agent.
    """
    selected_topic: str
    is_broad: bool