import logging
import random
from typing import Optional
from sqlalchemy.orm import Session
from influxdb_client import Point
from datetime import datetime, timezone

from api.db import crud
from api.db.influx_client import write_api, INFLUXDB_BUCKET, INFLUXDB_ORG

logger = logging.getLogger("CryptoMugAPI")

def fetch_and_store_prices(db: Session, provider_id: Optional[int] = None) -> dict:
    """
    Fetches prices for all enabled tokens from a provider and stores them in InfluxDB.
    """
    # 1. Get the provider
    if provider_id:
        provider = crud.get_provider(db, provider_id=provider_id)
        if not provider:
            raise ValueError(f"Provider with id {provider_id} not found.")
    else:
        provider = crud.get_default_provider(db)
        if not provider:
            raise ValueError("No default provider is set.")

    logger.info(f"Using provider '{provider.name}' to fetch prices.")

    # 2. Get all enabled tokens
    enabled_tokens = crud.get_enabled_tokens(db)
    if not enabled_tokens:
        logger.warning("No enabled tokens found. Nothing to fetch.")
        return {"message": "No enabled tokens found.", "provider": provider.name, "prices_written": 0}

    # 3. Fetch prices and create InfluxDB points
    price_points = []
    request_timestamp = datetime.now(timezone.utc)

    for token in enabled_tokens:
        # In a real application, you would make an HTTP request to the provider's API here.
        # e.g., price = requests.get(f"{provider.api_url}/price/{token.symbol}").json()['price']
        simulated_price = round(random.uniform(1.0, 50000.0), 2)
        logger.info(f"Fetched price for {token.symbol}: {simulated_price}")

        point = Point("price") \
            .tag("token_id", token.id) \
            .tag("provider_name", provider.name) \
            .field("value", simulated_price) \
            .time(request_timestamp)
        price_points.append(point)

    # 4. Write points to InfluxDB
    if price_points:
        logger.info(f"Writing {len(price_points)} price points to InfluxDB bucket '{INFLUXDB_BUCKET}'.")
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=price_points)
    else:
        logger.warning("No price points to write to InfluxDB.")

    return {"message": "Price fetch successful.", "provider": provider.name, "prices_written": len(price_points)}