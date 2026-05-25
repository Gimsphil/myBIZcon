import os
from pydantic_settings import BaseSettings if False else object # Allow clean running

class Settings:
    PROJECT_NAME: str = "myBIZcon Backend"
    API_V1_STR: str = "/api/v1"
    
    # AI Engine Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    # Google API Config Paths
    GOOGLE_CREDENTIALS_PATH: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    GOOGLE_TOKEN_PATH: str = os.getenv("GOOGLE_TOKEN_PATH", "token.json")

settings = Settings()
