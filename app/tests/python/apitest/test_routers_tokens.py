
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.db import models

def test_create_token(test_client: TestClient):
    """Test creating a new token successfully."""
    response = test_client.post(
        "/tokens/",
        json={"id": "bitcoin", "name": "Bitcoin", "is_enabled": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "bitcoin"
    assert data["name"] == "Bitcoin"
    assert data["is_enabled"] is True

def test_create_duplicate_token(test_client: TestClient, db_session: Session):
    """Test that creating a token with a duplicate ID fails."""
    token = models.Token(id="bitcoin", name="Bitcoin")
    db_session.add(token)
    db_session.commit()

    response = test_client.post(
        "/tokens/",
        json={"id": "bitcoin", "name": "Bitcoin"},
    )
    assert response.status_code == 409

def test_read_tokens(test_client: TestClient, db_session: Session):
    """Test reading a list of tokens."""
    token1 = models.Token(id="bitcoin", name="Bitcoin")
    token2 = models.Token(id="ethereum", name="Ethereum")
    db_session.add_all([token1, token2])
    db_session.commit()

    response = test_client.get("/tokens/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "bitcoin"
    assert data[1]["id"] == "ethereum"

# def test_read_enabled_tokens(test_client: TestClient, db_session: Session):
#     """Test reading only enabled tokens."""
#     token1 = models.Token(id="bitcoin", name="Bitcoin", is_enabled=True)
#     token2 = models.Token(id="ethereum", name="Ethereum", is_enabled=False)
#     db_session.add_all([token1, token2])
#     db_session.commit()

#     response = test_client.get("/tokens/enabled/")
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["id"] == "bitcoin"

def test_read_token(test_client: TestClient, db_session: Session):
    """Test reading a single token by its ID."""
    token = models.Token(id="bitcoin", name="Bitcoin")
    db_session.add(token)
    db_session.commit()

    response = test_client.get("/tokens/bitcoin")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "bitcoin"

def test_enable_disable_token(test_client: TestClient, db_session: Session):
    """Test enabling and disabling a token."""
    token = models.Token(id="bitcoin", name="Bitcoin", is_enabled=False)
    db_session.add(token)
    db_session.commit()

    # Enable
    response = test_client.post("/tokens/bitcoin/enable")
    assert response.status_code == 200
    assert response.json()["is_enabled"] is True

    # Disable
    response = test_client.post("/tokens/bitcoin/disable")
    assert response.status_code == 200
    assert response.json()["is_enabled"] is False

def test_update_token(test_client: TestClient, db_session: Session):
    """Test updating a token's details."""
    token = models.Token(id="bitcoin", name="Bitcoin", description="Old description")
    db_session.add(token)
    db_session.commit()

    response = test_client.put(
        "/tokens/bitcoin",
        json={"description": "New description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "New description"

def test_delete_token(test_client: TestClient, db_session: Session):
    """Test deleting a token."""
    token = models.Token(id="bitcoin", name="Bitcoin")
    db_session.add(token)
    db_session.commit()

    response = test_client.delete("/tokens/bitcoin")
    assert response.status_code == 204

    deleted_token = db_session.query(models.Token).filter_by(id="bitcoin").first()
    assert deleted_token is None
