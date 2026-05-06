from pydantic import BaseModel, Field
from datetime import datetime

class Project(BaseModel):
    project_id: str
    file_name: str
    file_size: int
    language: str
    chunk_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)