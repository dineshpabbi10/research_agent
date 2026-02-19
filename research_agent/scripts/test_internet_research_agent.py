import asyncio

from langchain.messages import HumanMessage
from research_agent.utils.config import ResearchAgentConfig
from research_agent.models.internet_research import InternetSearchQueryModel
from research_agent.tools.internet_research import internet_research_tools
from research_agent.prompts.internet_research import INTERNET_RESEARCH_SYSTEM_PROMPT
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

async def test_internet_research_agent():
    # Initialize model
    model = ChatOpenAI(model=ResearchAgentConfig().model_name)
    model = model.bind_tools(internet_research_tools)
    print("Creating Internet Research Agent with model:", ResearchAgentConfig().model_name)

    # Create agent
    internet_research_agent = create_agent(
        model=model,
        tools=internet_research_tools,
        system_prompt=INTERNET_RESEARCH_SYSTEM_PROMPT,
        state_schema=InternetSearchQueryModel,
    )

    input_state : InternetSearchQueryModel = {
        "messages": [HumanMessage("Start for topic Role of AI agents in ecommerce")],
        "selected_topic": "Role of AI agents in ecommerce",
        "search_queries": None,
        "relevant_blog_post_links": None,
        "seo_results": None
    }
    
    # Run the agent in a loop until all tools are used or no tool calls remain
    state = input_state
    max_iterations = 10
    iteration = 0
    

    output = await internet_research_agent.ainvoke(input=state)
    
    for message in output.get("messages", []):
        message.pretty_print()
    
    print(model.invoke(f"Given the context : {output} , Can you write a blog post for topic : Start for topic Role of AI agents in ecommerce"))



# Run the test
asyncio.run(test_internet_research_agent())
