import logging
import random
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from influxdb_client.client.write.point import Point
from datetime import datetime, timezone
from api.core.schemas import Token, Provider

from api.db import crud
from api.db import influx_client
from api.db.influx_client import single_client

logger = logging.getLogger("CryptoMugAPI")


async def fetch_prices(provider: Provider, tokens: List[str]) -> List[Dict[str, str]]:
    """
    Simulates fetching prices for a list of tokens from a given provider.

    In a real application, this function would make HTTP requests to the provider's API.

    Args:
        provider: The provider to use for fetching prices.
        tokens: A list of tokens to fetch prices for.

    Returns:
        A list of dictionaries, each containing token and price information.
    """
    fetched_data = []
    for token in tokens:
        # e.g., price = requests.get(f"{provider.api_url}/price/{token.symbol}").json()['price']
        simulated_price = round(random.uniform(1.0, 50000.0), 2)
        logger.info(f"Fetched price for {token} from {provider.name}: {simulated_price}")
        fetched_data.append({
            "token": token,
            "price": simulated_price
        })
    return fetched_data

def store_prices(price_data: List[Dict[str, str]], timestamp: datetime):
    """
    Converts price data into InfluxDB points and writes them to the database.

    Args:
        price_data: A list of dictionaries containing token, provider, and price.
        timestamp: The timestamp to associate with the price points.
    """
    price_points = []
    for data in price_data:
        point = Point("price") \
            .tag("token_id", data["token"]) \
            .field("value", data["price"]) \
            .time(timestamp)
        price_points.append(point)

    single_client.write_prices(price_points)
