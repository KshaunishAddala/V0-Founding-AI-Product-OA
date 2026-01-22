"""
News Service - Fetches and caches tech news from NewsAPI.
"""
import httpx
from fastapi import APIRouter, HTTPException, Depends

from app.config import Settings, get_settings
from app.models import Article, ArticlesResponse
from app.cache import news_cache

router = APIRouter(prefix="/api", tags=["news"])


class NewsService:
    def __init__(self, settings: Settings):
        self.api_key = settings.news_api_key
        self.base_url = settings.news_api_base_url

    async def fetch_articles(self, query: str | None = None) -> list[dict]:
        # Check cache first
        cache_key = f"news:{query or 'top'}"
        cached = news_cache.get(cache_key)
        if cached:
            return cached

        params = {
            "apiKey": self.api_key,
            "language": "en",
            "pageSize": 20,
        }

        if query:
            endpoint = f"{self.base_url}/everything"
            params["q"] = query
            params["sortBy"] = "publishedAt"
        else:
            endpoint = f"{self.base_url}/top-headlines"
            params["category"] = "technology"
            params["country"] = "us"

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params, timeout=10.0)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"News API error: {response.text}"
            )

        data = response.json()
        articles = data.get("articles", [])
        
        # Cache the results
        news_cache.set(cache_key, articles)
        
        return articles

    def parse_articles(self, raw_articles: list[dict]) -> list[Article]:
        articles = []
        for item in raw_articles:
            title = item.get("title")
            if not title or title == "[Removed]":
                continue

            articles.append(Article(
                title=title,
                description=item.get("description"),
                url=item.get("url", ""),
                thumbnail=item.get("urlToImage"),
                published_at=item.get("publishedAt", ""),
                source=item.get("source", {}).get("name", "Unknown")
            ))
        return articles


def get_news_service(settings: Settings = Depends(get_settings)) -> NewsService:
    return NewsService(settings)


@router.get("/articles", response_model=ArticlesResponse)
async def get_articles(service: NewsService = Depends(get_news_service)):
    """Fetch latest tech news articles. Results are cached for 15 minutes."""
    raw_articles = await service.fetch_articles()
    articles = service.parse_articles(raw_articles)
    return ArticlesResponse(articles=articles)
