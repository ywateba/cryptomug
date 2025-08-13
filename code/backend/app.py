import os
import time
import requests
import logging
from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# --- Logger Setup ---
# Create a custom logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# --- Configuration ---
# A list of cryptocurrency IDs from the CoinGecko API.
# You can find these IDs on the CoinGecko website (e.g., 'bitcoin', 'ethereum', 'tether').
CRYPTO_IDS = ["bitcoin", "ethereum", "ripple", "cardano", "solana"]

# Time interval for fetching data, in seconds. 300 seconds = 5 minutes.
FETCH_INTERVAL = 300

# Get InfluxDB connection details from environment variables
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# --- InfluxDB Client Setup ---
# It's good practice to check if the required environment variables are set.
if not all([INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET]):
    logger.error("InfluxDB environment variables (TOKEN, ORG, BUCKET) are not set.")
    exit(1)

# Instantiate the InfluxDB client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

# Instantiate the WriteAPI. SYNCHRONOUS mode ensures that data is written
# immediately, which is fine for this low-frequency task.
write_api = client.write_api(write_options=SYNCHRONOUS)

def fetch_and_write_prices():
    """
    Fetches cryptocurrency prices from the CoinGecko API and writes them
    to the InfluxDB database.
    """
    logger.info(f"Fetching prices for: {', '.join(CRYPTO_IDS)}")

    # Prepare the API request
    # We join the list of IDs into a comma-separated string for the API call.
    ids_string = ",".join(CRYPTO_IDS)
    api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_string}&vs_currencies=usd"

    try:
        # Make the API request
        response = requests.get(api_url)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        price_data = response.json()

        # Prepare the data points to be written to InfluxDB
        points = []
        for crypto_id, data in price_data.items():
            price = data.get("usd")
            if price is not None:
                # Create a data point for InfluxDB
                # 'measurement' is like a table name in SQL.
                # 'tags' are indexed columns, good for filtering (e.g., by crypto name).
                # 'fields' are the actual data values (e.g., the price).
                point = (
                    Point("crypto_price")
                    .tag("crypto_id", crypto_id)
                    .field("price_usd", float(price))
                    .time(datetime.utcnow())
                )
                points.append(point)
            else:
                logger.warning(f"No USD price found for {crypto_id}")

        # Write the data to InfluxDB
        if points:
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
            logger.info(f"Successfully wrote {len(points)} data points to InfluxDB.")
        else:
            logger.info("No data points to write.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from CoinGecko API: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

# --- Main Loop ---
if __name__ == "__main__":
    logger.info("Starting cryptocurrency price tracking service...")
    while True:
        fetch_and_write_prices()
        logger.info(f"Waiting for {FETCH_INTERVAL} seconds before next fetch...")
        time.sleep(FETCH_INTERVAL)
