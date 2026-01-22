# Tech Pulse

A website that summarizes the hottest tech news using AI.

<img width="1901" height="962" alt="image" src="https://github.com/user-attachments/assets/31bafe7a-5ca9-4790-bcff-521c590fb83c" />


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

### Development Process with AI

1. **High-level design**: Sketched out the initial architecture and feature requirements
2. **Architecture planning**: Defined the overall system structure (React frontend, FastAPI backend)
3. **Ideation with Cursor**: Provided feature ideas and requirements to Cursor for implementation suggestions
4. **Feedback loop**: Reviewed generated code, provided corrections and refinements
5. **Finalized design**: Reworked the architecture based on feedback into a monolithic frontend with microservice-style backend
6. **Implementation**: Used Cursor to generate the service layer, caching, and API endpoints
7. **Manual debugging**: Debugged core files and fixed integration issues hands-on
8. **Architecture refinement**: Restructured into clean service boundaries (news, summary, stocks)
9. **Final polish**: Added proper documentation, comments, and error handling
10. **Deployment**: Pushed to GitHub with proper .gitignore and environment variable handling

## What I'd Build Next

With more time:
- **Redis caching**: Replace in-memory cache for distributed deployments
- **Background jobs**: Prefetch news every 15 minutes so responses are always instant
- **Multiple news sources**: Aggregate from Hacker News, Reddit, RSS feeds; deduplicate similar stories
- **User accounts**: Save topic preferences, bookmark articles, email digests
- **WebSocket updates**: Push new articles in real-time
- **Full-text search**: Search across cached articles by keyword and date range

## Future Deployment Architecture

### Containerized Deployment on AWS

Each service would be containerized and deployed on EC2 instances:

```
                    ┌─────────────────┐
                    │   Route 53      │
                    │   (DNS)         │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   CloudFront    │
                    │   (CDN)         │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───────┐     │     ┌────────▼────────┐
     │  S3 (Frontend) │     │     │  API Gateway    │
     │  Static Assets │     │     │  (Auth + Rate   │
     └────────────────┘     │     │   Limiting)     │
                            │     └────────┬────────┘
                            │              │
                    ┌───────▼──────────────▼───────┐
                    │         ALB                   │
                    │   (Application Load Balancer) │
                    └───────┬──────────────┬───────┘
                            │              │
           ┌────────────────┼──────────────┼────────────────┐
           │                │              │                │
  ┌────────▼───────┐ ┌──────▼─────┐ ┌──────▼─────┐ ┌───────▼──────┐
  │ News Service   │ │  Summary   │ │  Stocks    │ │   Redis      │
  │ (ECS/Fargate)  │ │  Service   │ │  Service   │ │   (Cache)    │
  └────────────────┘ └────────────┘ └────────────┘ └──────────────┘
```

**Container Setup:**
- Each service (news, summary, stocks) runs in its own Docker container
- Deploy via ECS with Fargate (serverless containers) or EC2 launch type
- Services communicate internally via service discovery or ALB routing

### Scaling Strategy

**Traffic Analysis:**
- News endpoint: High read volume, cacheable → scale based on request count
- Summary endpoint: CPU-intensive (OpenAI calls), lower volume → scale based on CPU
- Stocks endpoint: Moderate volume, external API dependent → scale based on request count

**Auto Scaling Group Configuration:**
```
News Service ASG:
  - Min: 2, Max: 10, Desired: 2
  - Scale out: CPU > 70% or requests > 1000/min
  - Scale in: CPU < 30% for 10 minutes

Summary Service ASG:
  - Min: 1, Max: 5, Desired: 1
  - Scale out: CPU > 60% or latency > 3s
  - Scale in: CPU < 20% for 15 minutes

Stocks Service ASG:
  - Min: 1, Max: 3, Desired: 1
  - Scale out: Requests > 500/min
  - Scale in: Requests < 100/min for 10 minutes
```

### Authentication Layer

**Do we need auth?** If we want user-specific features (saved preferences, bookmarks, personalized feeds), yes.

**Implementation with API Gateway:**
- AWS API Gateway sits in front of the ALB
- JWT validation at the gateway level (zero changes to backend services)
- Tokens issued by AWS Cognito or custom auth service

```
Request Flow:
Client → API Gateway (JWT validation) → ALB → Services
```

**JWT Structure:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "roles": ["user"],
  "exp": 1234567890
}
```

### Social Authentication Providers

**Do we need social login?** For better UX and reduced friction, likely yes.

**Options via AWS Cognito:**
- Google OAuth 2.0
- Apple Sign In
- GitHub (relevant for tech audience)
- Email/password as fallback

**Implementation:**
- Cognito User Pool handles all OAuth flows
- Frontend uses Amplify SDK or direct Cognito API
- Backend validates Cognito-issued JWTs

### File Upload Architecture

**Do we need uploads?** If users can submit articles, upload profile pictures, or attach content, yes.

**Recommended Approach: S3 with Presigned URLs**

```
Upload Flow:
1. Client requests upload URL from backend
2. Backend generates presigned S3 URL (valid 15 min)
3. Client uploads directly to S3 (no backend bandwidth)
4. S3 triggers Lambda for processing (resize, scan, etc.)
5. Backend stores S3 key in database
```

**Storage Options:**
| Use Case | Storage | Why |
|----------|---------|-----|
| User avatars | S3 + CloudFront | Fast CDN delivery, image processing |
| Article attachments | S3 | Cost-effective, scalable |
| User preferences | DynamoDB | Fast key-value lookups |
| Bookmarks/history | DynamoDB or PostgreSQL | Depends on query patterns |

**Security:**
- Presigned URLs expire after 15 minutes
- S3 bucket is private, no public access
- Virus scanning via Lambda on upload
- File type validation on both client and server
