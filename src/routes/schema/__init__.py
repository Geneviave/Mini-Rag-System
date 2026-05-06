# TIP: Initialize package exports here.
from pydantic import BaseModel
class UploadResponse(BaseModel):
    project_id: str
    message: str
class ProcessResponse(BaseModel):
    project_id: str
    chunk_count: int
    message: str
class SearchRequest(BaseModel):
    question: str
class SearchResponse(BaseModel):
    answer: str
    sources: list