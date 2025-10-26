from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db import models

def test_create_provider(test_client: TestClient):
    """Test creating a new provider successfully."""
    response = test_client.post(
        "/providers/",
        json={
            "name": "CoinGecko",
            "api_url": "https://api.coingecko.com/api/v3",
            "auth_method": "none",
            "token_mapping": {"bitcoin": "bitcoin", "ethereum": "ethereum"}
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "CoinGecko"
    assert data["is_default"] is False
    assert "id" in data

def test_create_duplicate_provider(test_client: TestClient, db_session: Session):
    """Test that creating a provider with a duplicate name fails."""
    # Create initial provider
    provider = models.Provider(name="CoinGecko", api_url="...", auth_method="none")
    db_session.add(provider)
    db_session.commit()

    # Attempt to create another with the same name
    response = test_client.post(
        "/providers/",
        json={"name": "CoinGecko", "api_url": "...", "auth_method": "none"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Provider with this name already exists"

def test_read_providers(test_client: TestClient, db_session: Session):
    """Test reading a list of providers."""
    provider1 = models.Provider(name="Provider1", api_url="...", auth_method="none")
    provider2 = models.Provider(name="Provider2", api_url="...", auth_method="none")
    db_session.add_all([provider1, provider2])
    db_session.commit()

    response = test_client.get("/providers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Provider1"
    assert data[1]["name"] == "Provider2"

def test_read_provider(test_client: TestClient, db_session: Session):
    """Test reading a single provider by its ID."""
    provider = models.Provider(name="TestProvider", api_url="...", auth_method="none")
    db_session.add(provider)
    db_session.commit()

    response = test_client.get(f"/providers/{provider.name}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestProvider"
    assert data["id"] == provider.id

def test_read_nonexistent_provider(test_client: TestClient):
    """Test that reading a non-existent provider by name returns a 404."""
    response = test_client.get("/providers/non-existent-provider")
    assert response.status_code == 404

def test_set_default_provider(test_client: TestClient, db_session: Session):
    """Test setting a provider as the default."""
    p1 = models.Provider(name="P1", api_url="...", auth_method="none", is_default=True)
    p2 = models.Provider(name="P2", api_url="...", auth_method="none", is_default=False)
    db_session.add_all([p1, p2])
    db_session.commit()
    db_session.refresh(p1)
    db_session.refresh(p2)

    # Set p2 as the new default
    response = test_client.post(f"/providers/{p2.name}/set-default")
    assert response.status_code == 200
    assert response.json()["is_default"] is True

    # Verify in DB
    db_session.refresh(p1)
    db_session.refresh(p2)
    assert p1.is_default is False
    assert p2.is_default is True

def test_update_provider(test_client: TestClient, db_session: Session):
    """Test updating a provider's details."""
    provider = models.Provider(name="Original", api_url="original_url", auth_method="none")
    db_session.add(provider)
    db_session.commit()

    response = test_client.put(
        f"/providers/{provider.name}",
        json={"api_url": "updated_url"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["api_url"] == "updated_url"
    assert data["name"] == "Original" # Name should not change

def test_delete_provider(test_client: TestClient, db_session: Session):
    """Test deleting a provider."""
    provider = models.Provider(name="ToDelete", api_url="...", auth_method="none")
    db_session.add(provider)
    db_session.commit()
    provider_name = provider.name

    response = test_client.delete(f"/providers/{provider_name}")
    assert response.status_code == 204

    # Verify it's gone from the database
    deleted_provider = db_session.query(models.Provider).filter_by(name=provider_name).first()
    assert deleted_provider is None