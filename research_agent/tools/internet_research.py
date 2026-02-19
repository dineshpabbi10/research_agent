from typing import Counter
from urllib.parse import urlparse

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolRuntime
import requests
import trafilatura
import yake

from research_agent.models.internet_research import Headings, InternetSearchQueryModel, Links, SEOAnalysisResult
from research_agent.prompts.topic_selection import TOPIC_SELECTION_SYSTEM_PROMPT
from research_agent.utils.config import ResearchAgentConfig
from langchain_core.tools import ToolException, tool
from langgraph.types import Command
from bs4 import BeautifulSoup
from textstat import textstat
import asyncio
import tavily  # assuming you have tavily installed and configured
from typing import cast, Dict, Any

@tool
async def search_internet_with_tavily(runtime: ToolRuntime):
    """
    Given search queries in state, return top 3 web links for each query.
    Updates `relevant_blog_post_links` in state.
    """
    search_queries: list[str] = runtime.state.get("search_queries", [])
    if not search_queries or not all(isinstance(q, str) for q in search_queries):
        raise ToolException("No valid search queries found in state")

    all_links = []

    async def search_query(query: str) -> list[str]:
        try:
            client = tavily.AsyncTavilyClient()
            results = await client.search(query, num_results=3)
            links = [cast(Dict[str, Any], r)["link"] for r in results if isinstance(r, dict) and "link" in r]

            return links
        except Exception as e:
            return []

    tasks = [search_query(q) for q in search_queries]
    results_per_query = await asyncio.gather(*tasks)

    # Flatten results
    for links in results_per_query:
        all_links.extend(links)

    return Command(update={"relevant_blog_post_links": all_links})

@tool
async def get_search_query(runtime: ToolRuntime):
    """
    Given a user query, get 5 search queries to search internet for 

    Args:
        topic : str 
            The topic to search for
    
    Returns:
        list[str] : list of search queries
    """
    topic = runtime.state.get("selected_topic",None)
    if topic is None:
        raise ToolException("selected_topic is None")
    model = ChatOpenAI(model=ResearchAgentConfig().model_name)
    model = model.with_structured_output(InternetSearchQueryModel)

    result = model.invoke(TOPIC_SELECTION_SYSTEM_PROMPT.format(user_topic=topic))

    output = InternetSearchQueryModel.model_validate(result)

    return Command(update={"search_queries": output})

async def analyze_seo_of_webpage(url: str) -> SEOAnalysisResult:
    """
    Analyze SEO of a webpage from a given url
    """
    # -------- Fetch HTML --------
    html = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    # -------- Extract Clean Article Text --------
    downloaded = trafilatura.fetch_url(url)
    article_text = trafilatura.extract(downloaded) or ""

    words = article_text.split()
    word_count = len(words)

    # -------- Keyword Extraction --------
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=20)
    keywords = kw_extractor.extract_keywords(article_text)

    keyword_freq = Counter(words)
    top_keywords = dict(keyword_freq.most_common(20))

    # -------- Meta & Structure --------
    title = soup.title.string if soup.title else None

    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"] if meta_desc_tag else None

    h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]
    h3_tags = [h.get_text(strip=True) for h in soup.find_all("h3")]

    # -------- Links Analysis --------
    domain = urlparse(url).netloc
    internal_links = 0
    external_links = 0

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if domain in href:
            internal_links += 1
        elif isinstance(a['href'],str) and str(a['href']).startswith("http"):
            external_links += 1

    # -------- Readability --------
    readability_score = textstat.flesch_reading_ease(article_text)

    seo_result = SEOAnalysisResult(
        url=url,
        title=title,
        meta_description=str(meta_description) if meta_description else None,
        word_count=word_count,
        top_keywords_frequency=top_keywords,
        yake_keywords=keywords,
        headings=Headings(
            h1=h1_tags,
            h2=h2_tags,
            h3=h3_tags,
        ),
        links=Links(
            internal=internal_links,
            external=external_links,
        ),
        readability_score=readability_score,
    )

    return seo_result

@tool
async def analyze_links_seo(runtime: ToolRuntime):
    """
    Analyze SEO statistics of blog link urls to make decision on 
    """
    urls = runtime.state.get("relevant_blog_post_links",[])
    urls = list(map(str, urls)) if urls else []
    if not urls:
        return ToolException("No urls found. We need to fetch blog urls first")
    
    tasks = [analyze_seo_of_webpage(url) for url in urls]
    results = await asyncio.gather(*tasks)

    return  Command(update={"seo_results" : results})


internet_research_tools = [search_internet_with_tavily,get_search_query,analyze_links_seo]