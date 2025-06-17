import httpx
from src.config.manager import settings

BASE_URL = "https://api.polygon.io/v2/aggs/ticker"

async def fetch_aggregates(ticker: str, multiplier: int, timespan: str, _from: str, to: str):
    url = f"{BASE_URL}/{ticker}/range/{multiplier}/{timespan}/{_from}/{to}"
    params = {"apiKey": settings.POLYGON_API_KEY}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    return data["results"]
