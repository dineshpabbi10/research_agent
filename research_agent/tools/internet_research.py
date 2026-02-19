from typing import Counter, Dict, Any, List, Tuple, cast
from urllib.parse import urlparse
import asyncio

import requests
import trafilatura
import yake
from bs4 import BeautifulSoup
from textstat import textstat
import tavily

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command
from langchain_core.tools import ToolException, tool
from langchain_core.messages import ToolMessage

from research_agent.models.internet_research import (
    Headings,
    Links,
    SEOAnalysisResult,
    InternetSearchQueryModel,
)
from research_agent.prompts.topic_selection import TOPIC_SELECTION_SYSTEM_PROMPT
from research_agent.utils.config import ResearchAgentConfig

# --------------------------- TOOL: GET SEARCH QUERIES ---------------------------

@tool
async def get_search_query(runtime: ToolRuntime) -> Command:
    """
    Generate 5 search queries for the user-selected topic.
    Returns search_queries in state and a ToolMessage for hints.
    """
    tool_id = runtime.tool_call_id or "get_search_query"
    topic = runtime.state.get("selected_topic")
    
    if not topic:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="selected_topic is missing. Ask user to provide a topic.",
                        tool_call_id=tool_id,
                        status="error"
                    )
                ]
            }
        )

    # Call LLM to generate queries
    model = ChatOpenAI(model=ResearchAgentConfig().model_name)
    model = model.with_structured_output(InternetSearchQueryModel)
    try:
        result = model.invoke(TOPIC_SELECTION_SYSTEM_PROMPT.format(user_topic=topic))
        output = InternetSearchQueryModel.model_validate(result)
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error generating search queries: {str(e)}",
                        tool_call_id=tool_id,
                        status="error"
                    )
                ]
            }
        )

    return Command(
        update={
            "search_queries": output.search_queries,
            "messages": [
                ToolMessage(
                    content=f"Generated {len(output.search_queries)} search queries for topic '{topic}'.",
                    tool_call_id=tool_id,
                    status="success"
                )
            ]
        }
    )


# --------------------------- TOOL: SEARCH INTERNET WITH TAVILY ---------------------------

@tool
async def search_internet_with_tavily(runtime: ToolRuntime) -> Command:
    """
    Given search queries in state, return top 3 web links per query.
    Updates `relevant_blog_post_links` in state.
    """
    tool_id = runtime.tool_call_id or "search_internet_with_tavily"
    search_queries: list[str] = runtime.state.get("search_queries", [])

    if not search_queries or not all(isinstance(q, str) for q in search_queries):
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="No valid search queries found in state. Run get_search_query first.",
                        tool_call_id=tool_id,
                        status="error"
                    )
                ]
            }
        )

    all_links: list[str] = []

    async def search_query(query: str) -> list[str]:
        try:
            client = tavily.AsyncTavilyClient()
            results = await client.search(query, num_results=3)
            links: list[str] = [
                cast(Dict[str, Any], r)["link"]
                for r in results
                if isinstance(r, dict) and "link" in r
            ]
            return links
        except Exception:
            return []

    tasks = [search_query(q) for q in search_queries]
    results_per_query = await asyncio.gather(*tasks)

    # Flatten results
    for links in results_per_query:
        all_links.extend(links)

    return Command(
        update={
            "relevant_blog_post_links": all_links,
            "messages": [
                ToolMessage(
                    content=f"Found {len(all_links)} links from {len(search_queries)} search queries.",
                    tool_call_id=tool_id,
                    status="success"
                )
            ]
        }
    )


# --------------------------- HELPER: ANALYZE SEO OF SINGLE PAGE ---------------------------

async def analyze_seo_of_webpage(url: str) -> SEOAnalysisResult:
    """
    Analyze SEO of a webpage from a given URL.
    """
    # Fetch HTML
    html = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")

    # Extract article text
    downloaded = trafilatura.fetch_url(url)
    article_text = trafilatura.extract(downloaded) or ""
    words = article_text.split()
    word_count = len(words)

    # Keyword Extraction
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=20)
    keywords = kw_extractor.extract_keywords(article_text)
    keyword_freq = Counter(words)
    top_keywords = dict(keyword_freq.most_common(20))

    # Meta & Headings
    title = soup.title.string if soup.title else None
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"] if meta_desc_tag else None
    h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]
    h3_tags = [h.get_text(strip=True) for h in soup.find_all("h3")]

    # Links
    domain = urlparse(url).netloc
    internal_links = 0
    external_links = 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if domain in href:
            internal_links += 1
        elif isinstance(href, str) and href.startswith("http"):
            external_links += 1

    # Readability
    readability_score = textstat.flesch_reading_ease(article_text)

    return SEOAnalysisResult(
        url=url,
        title=title,
        meta_description=str(meta_description) if meta_description else None,
        word_count=word_count,
        top_keywords_frequency=top_keywords,
        yake_keywords=keywords,
        headings=Headings(h1=h1_tags, h2=h2_tags, h3=h3_tags),
        links=Links(internal=internal_links, external=external_links),
        readability_score=readability_score
    )


# --------------------------- TOOL: ANALYZE LINKS SEO ---------------------------

@tool
async def analyze_links_seo(runtime: ToolRuntime) -> Command:
    """
    Analyze SEO of blog URLs from state.
    """
    tool_id = runtime.tool_call_id or "analyze_links_seo"
    urls: list[str] = runtime.state.get("relevant_blog_post_links", [])
    urls = list(map(str, urls)) if urls else []

    if not urls:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="No blog links found in state. Run search_internet_with_tavily first.",
                        tool_call_id=tool_id,
                        status="error"
                    )
                ]
            }
        )

    tasks = [analyze_seo_of_webpage(url) for url in urls]
    try:
        results = await asyncio.gather(*tasks)
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error analyzing SEO: {str(e)}",
                        tool_call_id=tool_id,
                        status="error"
                    )
                ]
            }
        )

    return Command(
        update={
            "seo_results": results,
            "messages": [
                ToolMessage(
                    content=f"Analyzed SEO for {len(results)} URLs.",
                    tool_call_id=tool_id,
                    status="success"
                )
            ]
        }
    )


# --------------------------- REGISTER TOOLS ---------------------------

internet_research_tools = [
    get_search_query,
    search_internet_with_tavily,
    analyze_links_seo
]
