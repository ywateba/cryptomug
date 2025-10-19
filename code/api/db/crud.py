import logging
from api.core import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from api.db import schemas

logger = logging.getLogger("CryptoMugAPI")

# --- Provider CRUD ---

def get_provider(db: Session, provider_id: int):
    return db.query(models.Provider).filter(models.Provider.id == provider_id).first()

def get_provider_by_name(db: Session, name: str):
    return db.query(models.Provider).filter(models.Provider.name == name).first()

def get_providers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Provider).offset(skip).limit(limit).all()

def get_default_provider(db: Session):
    return db.query(models.Provider).filter(models.Provider.is_default == True).first()

def create_provider(db: Session, provider: schemas.ProviderCreate):
    db_provider = models.Provider(**provider.model_dump(exclude={"is_default"}))
    logger.info(f"Creating new provider: {provider.name}")
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def set_default_provider(db: Session, db_provider: models.Provider):
    logger.info(f"Setting provider {db_provider.name} as default.")
    # Unset current default
    current_default = get_default_provider(db)
    if current_default:
        logger.info(f"Unsetting current default provider: {current_default.name}")
        current_default.is_default = False
    
    # Set new default
    db_provider.is_default = True
    db.commit()
    db.refresh(db_provider)
    return db_provider

def update_provider(db: Session, db_provider: models.Provider, provider_update: schemas.ProviderUpdate):
    update_data = provider_update.model_dump(exclude_unset=True)
    logger.info(f"Updating provider {db_provider.name} with data: {update_data}")
    for key, value in update_data.items():
        setattr(db_provider, key, value)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def delete_provider(db: Session, db_provider: models.Provider):
    logger.info(f"Deleting provider: {db_provider.name}")
    db.delete(db_provider)
    db.commit()

# --- Token CRUD ---

def get_token(db: Session, token_id: str):
    return db.query(models.Token).filter(models.Token.id == token_id).first()

def get_tokens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Token).offset(skip).limit(limit).all()

def get_enabled_tokens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Token).filter(models.Token.is_enabled == True).offset(skip).limit(limit).all()

def create_token(db: Session, token: schemas.TokenCreate):
    # The 'is_enabled' flag from the create schema is respected here.
    db_token = models.Token(**token.model_dump())
    logger.info(f"Creating new token: {token.id}")
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def update_token(db: Session, db_token: models.Token, token_update: schemas.TokenUpdate):
    update_data = token_update.model_dump(exclude_unset=True)
    logger.info(f"Updating token {db_token.id} with data: {update_data}")
    for key, value in update_data.items():
        setattr(db_token, key, value)
    db.commit()
    db.refresh(db_token)
    return db_token

def delete_token(db: Session, db_token: models.Token):
    logger.info(f"Deleting token: {db_token.id}")
    db.delete(db_token)
    db.commit()

def set_token_enabled_status(db: Session, db_token: models.Token, enabled: bool):
    """Sets the enabled status of a token."""
    if enabled:
        logger.info(f"Enabling token: {db_token.id}")
    else:
        logger.info(f"Disabling token: {db_token.id}")

    db_token.is_enabled = enabled
    db.commit()
    db.refresh(db_token)
    return db_token