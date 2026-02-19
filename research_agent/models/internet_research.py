from pydantic import BaseModel

class InternetSearchQueryModel(BaseModel):
    search_queries : list[str]