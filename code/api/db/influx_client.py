import logging
from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import List
from api.config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET

logger = logging.getLogger("CryptoMugAPI")

# --- InfluxDB Client Setup ---

logger.info(f"Initializing InfluxDB client for org '{INFLUXDB_ORG}'")
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

class InfluxClient:
    def __init__(self):
        logger.info(f"Initializing InfluxDB client for org '{INFLUXDB_ORG}'")
        self.client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write_prices(self, points: List[Point]):
        """Writes a list of Point objects to InfluxDB."""
        if not points:
            logger.warning("No price points to write to InfluxDB.")
            return
        logger.info(f"Writing {len(points)} price points to InfluxDB bucket '{INFLUXDB_BUCKET}'.")
        self.write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
        logger.info(f"prices added")

# Create a single instance to be used across the application
single_client = InfluxClient()