from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path

# Base dir = Backend
BASE_DIR = Path(__file__).resolve().parents[2]

# load .env
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    GEMINI_API_KEY: str
    CHROMA_DIR: str
    #CHROMA_API_IMPL: str

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()

# Backwards-compatible Config class (used elsewhere in the project)
class Config:
    MONGO_URI = settings.MONGO_URI
    MONGO_DB_NAME = settings.MONGO_DB_NAME
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    CHROMA_DIR = settings.CHROMA_DIR
   # CHROMA_API_IMPL = settings.CHROMA_API_IMPL