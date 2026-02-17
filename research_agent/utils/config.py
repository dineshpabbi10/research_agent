from pydantic import Field
from pydantic_settings import BaseSettings


class ResearchAgentConfig(BaseSettings):
    """
    Configuration for the research agent.
    """

    # Add any configuration parameters you need here
    model_name: str = Field(
        default="gpt-4o",
        description="The name of the language model to use for the research agent.",
    )
