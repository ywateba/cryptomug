import logging
from api.db import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from api.core import schemas
from api.db.models import Provider




logger = logging.getLogger("CryptoMugAPI")

# --- Provider CRUD ---

def get_provider(db: Session, provider_id: int):
    return db.query(Provider).filter_by(id=provider_id).first()


def get_provider_by_name(db: Session, provider_name: str):
    return db.query(Provider).filter_by(name=provider_name).first()

def get_providers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Provider).offset(skip).limit(limit).all()

def get_default_provider(db: Session):
    return db.query(models.Provider).filter_by(is_default=True).first()

def create_provider(db: Session, provider: schemas.ProviderCreate):

    db_provider = Provider(**provider.dict(exclude={"is_default"}))
    logger.info(f"Creating new provider: {provider.name}")
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def set_default_provider(db: Session, provider: schemas.Provider):
    logger.info(f"Setting provider {provider.name} as default.")

    db_provider = get_provider_by_name(db, provider.name)

    # Unset current default
    current_default = get_default_provider(db)
    if current_default:
        logger.info(f"Unsetting current default provider: {current_default.name}")
        setattr(current_default, "is_default", False)
      
    
    # Set new default
    setattr(db_provider, "is_default", True)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def update_provider(db: Session, db_provider: Provider, provider_update: schemas.ProviderUpdate):

    update_data = provider_update.dict(exclude_unset=True)
    logger.info(f"Updating provider {db_provider.name} with data: {update_data}")
    for key, value in update_data.items():
        setattr(db_provider, key, value)
    db.commit()
    db.refresh(db_provider)
    return db_provider

def delete_provider(db: Session, provider_name):
    logger.info(f"Deleting provider: {provider_name}")

    db_provider = get_provider_by_name(db, provider_name)
    db.delete(db_provider)
    db.commit()