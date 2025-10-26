import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime, timezone

from api.db import influx_service
from api.core import schemas


class TestInfluxService(unittest.TestCase):

    @patch('api.db.influx_service.random.uniform')
    async def test_fetch_prices_simulation(self, mock_uniform):
        """Test the price fetching simulation logic."""
        # Arrange
        mock_uniform.return_value = 12345.6789
        provider = schemas.Provider(id="binance", name="Binance", api_url="", auth_method="none", is_default=True)
        tokens = ["bitcoin", "ethereum"]

        # Act
        result = await influx_service.fetch_prices(provider, tokens)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {"token": "bitcoin", "price": 12345.68})
        self.assertEqual(result[1], {"token": "ethereum", "price": 12345.68})
        self.assertEqual(mock_uniform.call_count, 2)

    @patch('api.db.influx_service.single_client')
    def test_store_prices(self, mock_influx_client):
        """Test that price data is correctly converted to Points and written."""
        # Arrange
        price_data = [
            {"token": "bitcoin", "price": 50000.0},
            {"token": "ethereum", "price": 4000.0}
        ]
        timestamp = datetime.now(timezone.utc)

        # Act
        influx_service.store_prices(price_data, timestamp)

        # Assert
        # Check that the client's write method was called once
        mock_influx_client.write_prices.assert_called_once()

        # Check the contents of the points passed to the write method
        written_points = mock_influx_client.write_prices.call_args[0][0]
        self.assertEqual(len(written_points), 2)

        # Verify the structure of the first point
        point1 = written_points[0].to_line_protocol()
        self.assertIn('price,token_id=bitcoin', point1)
        self.assertIn('value=50000.0', point1)
