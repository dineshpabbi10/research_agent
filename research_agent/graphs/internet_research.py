from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from research_agent.tools.internet_research import internet_research_tools
from research_agent.utils.config import ResearchAgentConfig

model = ChatOpenAI(model=ResearchAgentConfig().model_name)
internet_research_agent = create_agent(
    model=model,
    tools=internet_research_tools
)