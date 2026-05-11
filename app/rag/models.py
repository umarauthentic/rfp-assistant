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


class QueryRequest(BaseModel):
    query: str
    use_memory: bool = True
    use_documents: bool = True


class QueryResponse(BaseModel):
    answer: str
    from_memory: bool
    memory_matches: list[SearchResult]
    document_matches: list[SearchResult]


class SaveAnswerRequest(BaseModel):
    question: str
    answer: str
    tags: list[str] = Field(default_factory=list)
    approved: bool = True
    source_docs: list[str] = Field(default_factory=list)
