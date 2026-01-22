from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    news_api_key: str = ""
    openai_api_key: str = ""
    finnhub_api_key: str = ""
    
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    news_api_base_url: str = "https://newsapi.org/v2"
    finnhub_base_url: str = "https://finnhub.io/api/v1"
    
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 500
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
