"""
Summary Service - Generates AI-powered news summaries using OpenAI.
"""
from fastapi import APIRouter, HTTPException, Depends
from openai import OpenAI

from app.config import Settings, get_settings
from app.models import SummaryRequest, SummaryResponse
from app.cache import summary_cache
from services.news import NewsService, get_news_service

router = APIRouter(prefix="/api", tags=["summary"])


class SummaryService:
    def __init__(self, settings: Settings):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens

    def build_prompt(self, headlines: list[str], tags: list[str]) -> str:
        headlines_text = "\n".join(headlines)
        context = f"focusing on: {', '.join(tags)}" if tags else "in general tech"

        return f"""Here are today's top tech headlines {context}:

{headlines_text}

Write a concise 2-3 paragraph summary of the main trends and stories. Be informative and direct."""

    def extract_headlines(self, articles: list[dict], limit: int = 10) -> list[str]:
        headlines = []
        for article in articles[:limit]:
            title = article.get("title", "")
            if not title or title == "[Removed]":
                continue
            desc = (article.get("description") or "")[:150]
            headlines.append(f"- {title}: {desc}")
        return headlines

    def generate_summary(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a tech news analyst. Summarize news concisely and insightfully."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=0.7
        )
        return completion.choices[0].message.content or ""


def get_summary_service(settings: Settings = Depends(get_settings)) -> SummaryService:
    return SummaryService(settings)


@router.post("/summary", response_model=SummaryResponse)
async def get_summary(
    request: SummaryRequest,
    news_service: NewsService = Depends(get_news_service),
    summary_service: SummaryService = Depends(get_summary_service)
):
    """
    Generate an AI summary of current tech news.
    Optionally filter by tags (e.g., ["AI", "startups"]).
    Summaries are cached for 1 hour per unique tag combination.
    """
    # Create cache key from sorted tags
    cache_key = f"summary:{','.join(sorted(request.tags)) or 'general'}"
    cached = summary_cache.get(cache_key)
    if cached:
        return cached

    query = " OR ".join(request.tags) if request.tags else None
    raw_articles = await news_service.fetch_articles(query)

    if not raw_articles:
        raise HTTPException(status_code=404, detail="No articles found")

    headlines = summary_service.extract_headlines(raw_articles)
    if not headlines:
        raise HTTPException(status_code=404, detail="No valid headlines found")

    prompt = summary_service.build_prompt(headlines, request.tags)
    summary = summary_service.generate_summary(prompt)

    response = SummaryResponse(summary=summary, article_count=len(headlines))
    
    # Cache the response
    summary_cache.set(cache_key, response)
    
    return response
