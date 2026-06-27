from pydantic import BaseModel, Field
from typing import Any


class Chunk(BaseModel):
    id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResponseTag(BaseModel):
    label: str
    tag_type: str
    value: str
    score: float | None = None
    match_id: str | None = None


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    use_memory: bool = True
    use_documents: bool = True


class QueryResponse(BaseModel):
    answer: str
    from_memory: bool
    memory_matches: list[SearchResult]
    document_matches: list[SearchResult]
    response_tags: list[ResponseTag] = Field(default_factory=list)


class SaveAnswerRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    answer: str = Field(min_length=1, max_length=12000)
    tags: list[str] = Field(default_factory=list)
    approved: bool = True
    source_docs: list[str] = Field(default_factory=list)
