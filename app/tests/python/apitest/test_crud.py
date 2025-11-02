from httpx import get
import pytest
from sqlalchemy.orm import Session

from api.db.crud import providers, tokens
from api.db import models
from api.core import schemas

# --- Provider CRUD Tests ---

def test_create_provider(db_session: Session):
    provider_schema = schemas.ProviderCreate(name="TestProvider", 
                                             api_url="http://test.com",
                                             auth_method="none",
                                             is_default=False
                                             )
   
    provider = providers.create_provider(db_session, provider_schema)
    assert getattr(provider, "name") == "TestProvider"
    assert getattr(provider, "api_url") == "http://test.com"
    assert hasattr(provider, "id")
    assert isinstance(provider.id, str) and len(provider.id) == 36 # UUID4 string length



def test_get_providers(db_session: Session):
    db_session.add(models.Provider(name="P1", api_url="http://binance.com"))
    db_session.add(models.Provider(name="P2", api_url="http://coingecko.com"))
    db_session.commit()
    
    all_providers = providers.get_providers(db_session)
    assert len(all_providers) == 2

def test_get_provider_by_name(db_session: Session):
    db_session.add(models.Provider(name="FindMe", api_url="http://binance.com"))
    db_session.commit()

    provider = providers.get_provider_by_name(db_session, "FindMe")
    assert getattr(provider, "name") == "FindMe"


def test_set_default_provider(db_session: Session):
    p1 = models.Provider(name="P1", api_url="some_url_1", is_default=True)
    p2 = models.Provider(name="P2", api_url="some_url_2", is_default=False)
    db_session.add_all([p1, p2])
    db_session.commit()

    # Fetch the provider object to pass to the function
    provider_to_set = providers.get_provider_by_name(db_session, "P2")
    providers.set_default_provider(db_session, provider=provider_to_set)
    
    db_session.refresh(p1)
    db_session.refresh(p2)

    assert p1.is_default is False
    assert p2.is_default is True

def test_update_provider(db_session: Session):
    provider = models.Provider(name="Original", api_url="original_url")
    db_session.add(provider)
    db_session.commit()

    update_schema = schemas.ProviderUpdate(api_url="updated_url")
    updated_provider = providers.update_provider(db_session, provider, update_schema)

    assert getattr(updated_provider, "api_url") == "updated_url"
    assert getattr(updated_provider, "name") == "Original"


def test_delete_provider(db_session: Session):
    provider = models.Provider(name="ToDelete", api_url="...")
    db_session.add(provider)
    db_session.commit()

    provider_to_delete = providers.get_provider_by_name(db_session, "ToDelete")
    providers.delete_provider(db_session, provider_to_delete)
    assert db_session.query(models.Provider).count() == 0

# --- Token CRUD Tests ---

def test_create_token(db_session: Session):
    token_schema = schemas.TokenCreate(id="btc", name="Bitcoin", is_enabled=True)
    token = tokens.create_token(db_session, token_schema)
    assert getattr(token, "id") == "btc"
    assert getattr(token, "name") == "Bitcoin"
    assert token.is_enabled is True
    assert db_session.query(models.Token).count() == 1

def test_get_enabled_tokens(db_session: Session):
    t1 = models.Token(id="btc", name="Bitcoin", is_enabled=True)
    t2 = models.Token(id="eth", name="Ethereum", is_enabled=False)
    t3 = models.Token(id="ada", name="Cardano", is_enabled=True)
    db_session.add_all([t1, t2, t3])
    db_session.commit()

    enabled = tokens.get_enabled_tokens(db_session)
    enabled_ids = {token for token in enabled}
    assert enabled_ids == {"btc", "ada"}

def test_update_token(db_session: Session):
    token = models.Token(id="btc", name="Bitcoin", description="Old")
    db_session.add(token)
    db_session.commit()

    update_schema = schemas.TokenUpdate(description="New")
    updated_token = tokens.update_token(db_session, token, update_schema)
    
    assert getattr(updated_token, "description" ) == "New"

def test_set_token_enabled_status(db_session: Session):
    token = models.Token(id="btc", name="Bitcoin", is_enabled=False)
    db_session.add(token)
    db_session.commit()

    # Enable
    tokens.set_token_enabled_status(db_session, token, True)
    db_session.refresh(token)
    assert token.is_enabled is True

    # Disable
    tokens.set_token_enabled_status(db_session, token, False)
    db_session.refresh(token)
    assert token.is_enabled is False