"""
Tech Pulse API Gateway
Aggregates tech news and provides AI-powered summaries.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from services import news, summary, stocks

settings = get_settings()

app = FastAPI(
    title="Tech Pulse API",
    description="API for tech news aggregation and AI-powered summaries",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(summary.router)
app.include_router(stocks.router)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
