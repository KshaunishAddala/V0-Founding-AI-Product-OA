from pydantic import BaseModel


class Article(BaseModel):
    title: str
    description: str | None
    url: str
    thumbnail: str | None
    published_at: str
    source: str


class ArticlesResponse(BaseModel):
    articles: list[Article]


class SummaryRequest(BaseModel):
    tags: list[str] = []


class SummaryResponse(BaseModel):
    summary: str
    article_count: int


class Stock(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float


class StocksResponse(BaseModel):
    stocks: list[Stock]
