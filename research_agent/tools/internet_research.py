from langchain_openai import ChatOpenAI
def get_search_query(topic:str):
    """
    Given a user query, get 5 search queries to search internet for 

    Args:
        topic : str 
            The topic to search for
    
    Returns:
        list[str] : list of search queries
    """
    model = ChatOpenAI("gpt-4o")

