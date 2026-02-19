from pydantic import BaseModel, Field
from operator import add
from typing import Dict, List, Optional, Tuple,Annotated


class Headings(BaseModel):
    h1: List[str] = Field(default_factory=list)
    h2: List[str] = Field(default_factory=list)
    h3: List[str] = Field(default_factory=list)


class Links(BaseModel):
    internal: int
    external: int


class SEOAnalysisResult(BaseModel):
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None

    word_count: int

    # word -> frequency
    top_keywords_frequency: Dict[str, int]

    # YAKE returns list of tuples: (keyword, score)
    yake_keywords: List[Tuple[str, float]]

    headings: Headings
    links: Links

    readability_score: float

class InternetSearchQueryModel(BaseModel):
    search_queries : list[str]
    relevant_blog_post_links : list[str]
    seo_results : list[SEOAnalysisResult]


