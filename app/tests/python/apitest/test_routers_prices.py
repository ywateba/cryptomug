
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from api.db import models

@pytest.fixture
def setup_data(db_session: Session):
    """Fixture to set up a default provider and some tokens."""
    provider = models.Provider(name="DefaultProvider", api_url="...", auth_method="none", is_default=True)
    token1 = models.Token(id="bitcoin", name="Bitcoin", is_enabled=True)
    token2 = models.Token(id="ethereum", name="Ethereum", is_enabled=True)
    token3 = models.Token(id="cardano", name="Cardano", is_enabled=False)
    db_session.add_all([provider, token1, token2, token3])
    db_session.commit()
    return provider, [token1, token2]

def test_fetch_prices_with_default_provider(test_client: TestClient, setup_data):
    """Test fetching prices using the default provider."""
    with patch("api.db.influx_service.fetch_prices") as mock_fetch:
        mock_fetch.return_value = {"message": "Prices fetched for 2 tokens."}
        
        response = test_client.post("/prices/fetch")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Prices fetched for 2 tokens."}
        
        # Verify fetch_prices was called correctly
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0]
        assert call_args[0].name == "DefaultProvider"
        assert set(call_args[1]) == {"bitcoin", "ethereum"}

def test_fetch_prices_no_default_provider(test_client: TestClient, db_session: Session):
    """Test error when no default provider is set."""
    response = test_client.post("/prices/fetch")
    assert response.status_code == 500 # Based on how the exception is handled

def test_fetch_prices_no_enabled_tokens(test_client: TestClient, db_session: Session):
    """Test behavior when no tokens are enabled."""
    provider = models.Provider(name="DefaultProvider", api_url="...", auth_method="none", is_default=True)
    db_session.add(provider)
    db_session.commit()

    response = test_client.post("/prices/fetch")
    assert response.status_code == 200
    assert response.json()["message"] == "No enabled tokens found."

@patch("api.db.influx_service.fetch_prices", side_effect=ValueError("Provider API error"))
def test_fetch_prices_provider_error(mock_fetch, test_client: TestClient, setup_data):
    """Test that a provider error is handled and returns a 404."""
    response = test_client.post("/prices/fetch")
    assert response.status_code == 404
    assert response.json()["detail"] == "Provider API error"
