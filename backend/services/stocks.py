"""
Stocks Service - Fetches real-time stock quotes for AI companies from Finnhub.
"""
import asyncio
import httpx
from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models import Stock, StocksResponse

router = APIRouter(prefix="/api", tags=["stocks"])

AI_STOCK_SYMBOLS = ["NVDA", "MSFT", "GOOGL", "META", "AMD", "PLTR", "CRM", "SNOW"]


class StocksService:
    def __init__(self, settings: Settings):
        self.api_key = settings.finnhub_api_key
        self.base_url = settings.finnhub_base_url

    async def fetch_quote(self, client: httpx.AsyncClient, symbol: str) -> Stock | None:
        try:
            response = await client.get(
                f"{self.base_url}/quote",
                params={"symbol": symbol, "token": self.api_key},
                timeout=5.0
            )
            if response.status_code != 200:
                return None

            data = response.json()
            current_price = data.get("c")
            if not current_price:
                return None

            return Stock(
                symbol=symbol,
                price=round(current_price, 2),
                change=round(data.get("d") or 0, 2),
                change_percent=round(data.get("dp") or 0, 2)
            )
        except (httpx.RequestError, httpx.TimeoutException):
            return None

    async def fetch_all_quotes(self, symbols: list[str]) -> list[Stock]:
        """Fetch all stock quotes concurrently for better performance."""
        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_quote(client, symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks)
            return [stock for stock in results if stock is not None]


def get_stocks_service(settings: Settings = Depends(get_settings)) -> StocksService:
    return StocksService(settings)


@router.get("/stocks", response_model=StocksResponse)
async def get_stocks(service: StocksService = Depends(get_stocks_service)):
    """Fetch current stock prices for major AI companies."""
    stocks = await service.fetch_all_quotes(AI_STOCK_SYMBOLS)
    return StocksResponse(stocks=stocks)
