from pydantic_settings import BaseSettings
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "Regulatory Compliance Assistant"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173", 
        "http://localhost:3000",
        "https://compliance-ai-arvind.vercel.app"
    ]

    class Config:
        case_sensitive = True

settings = Settings()
