"""
TIP: Implement the Settings class using pydantic_settings to load configuration from the .env file.
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_EXTENSIONS: List[str]
    FILE_MAX_SIZE_MB: int
    FILE_CHUNK_SIZE: int
    MONGODB_URI: str
    MONGODB_DB_NAME: str
    OPENAI_API_KEY: str
    OPENAI_API_BASE: str
    GENERATE_RESPONSE_MODEL: str
    EMBEDDINGS_MODEL: str
    EMBEDDING_DIMENSION: int
    MAX_INPUT_TOKENS: int
    MAX_RESPONSE_TOKENS: int
    TEMPERATURE: float
    VECTOR_DB_PATH: str
    VECTOR_DISTANCE_METRIC: str
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()