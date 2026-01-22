# Tech Pulse

A website that summarizes the hottest tech news using AI.

## How to Run Locally

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Runs on http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:5173

## Setup / API Keys

Create a `.env` file in the `/backend` directory with the following environment variables:

```
NEWS_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
```

Where to get keys:
- **NewsAPI**: https://newsapi.org (free tier: 100 requests/day)
- **OpenAI**: https://platform.openai.com
- **Finnhub**: https://finnhub.io (free tier available)

## Approach and Tradeoffs

### Architecture
Built as a modular monolith with clear service boundaries:
- **News Service**: Fetches tech headlines from NewsAPI with 15-minute caching
- **Summary Service**: Generates AI summaries via GPT-4o-mini with 1-hour caching
- **Stocks Service**: Real-time AI company stock quotes from Finnhub

### Key Decisions

**In-memory caching over Redis**: Chose simplicity for this scope. News articles are cached for 15 minutes, summaries for 1 hour. This reduces API calls significantly while keeping content fresh. For production scale, Redis would be the upgrade path.

**GPT-4o-mini over GPT-4**: Cost-effective for summarization tasks while maintaining quality. The prompt is minimal - just headlines with optional topic filtering.

**NewsAPI as primary source**: Provides thumbnails and structured data out of the box. The 100 req/day free tier is a limitation, but caching mitigates this for development.

**No database**: All data is fetched fresh from external APIs and cached in memory. This keeps the architecture simple and ensures content is always current.

**FastAPI with dependency injection**: Services are injected via `Depends()`, making the code testable and the dependencies explicit.

## AI Tools Used

- **Cursor**: Used throughout development for code generation, refactoring, and debugging. Helped structure the microservices architecture and implement the caching layer.
- **OpenAI GPT-4o-mini**: Powers the news summarization feature within the application itself.

## What I'd Build Next

With more time:
- **Redis caching**: Replace in-memory cache for distributed deployments
- **Background jobs**: Prefetch news every 15 minutes so responses are always instant
- **Multiple news sources**: Aggregate from Hacker News, Reddit, RSS feeds; deduplicate similar stories
- **User accounts**: Save topic preferences, bookmark articles, email digests
- **WebSocket updates**: Push new articles in real-time
- **Full-text search**: Search across cached articles by keyword and date range
