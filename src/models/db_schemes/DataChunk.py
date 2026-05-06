from pydantic import BaseModel, Field
from datetime import datetime

class DataChunk(BaseModel):
    chunk_id: str
    source_file: str
    page_number: int
    section: str
    language: str
    text: str
    approx_tokens: int
    word_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)