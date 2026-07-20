# TIP: Initialize package exports here.
#b3rf el shape bta3 el input w el output bta3 el API
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