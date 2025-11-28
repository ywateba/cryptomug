import logging
from api.db import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from api.core import schemas
from api.db.models import Provider




logger = logging.getLogger("CryptoMugAPI")

# --- Provider CRUD ---

def get_provider_by_name(db: Session, provider_name: str):
    return db.query(Provider).filter_by(name=provider_name).first()

def get_providers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Provider).offset(skip).limit(limit).all()

def get_default_provider(db: Session):
    return db.query(models.Provider).filter_by(is_default=True).first()

def create_provider(db: Session, provider: schemas.ProviderCreate):

    db_provider = Provider(**provider.model_dump(exclude={"is_default"}))
    logger.info(f"Creating new provider: {provider.name}")
    try:
        db.add(db_provider)
        db.commit()
        db.refresh(db_provider)
        return db_provider
    except IntegrityError:
        db.rollback()
        logger.warning(f"IntegrityError on creating provider '{provider.name}'. It likely already exists.")
        raise

def set_default_provider(db: Session, provider: models.Provider):
    logger.info(f"Setting provider {provider.name} as default.")
    # Unset current default
    # This query is efficient and necessary to find the old default.
    current_default = get_default_provider(db)
    if current_default:
        logger.info(f"Unsetting current default provider: {current_default.name}")
        setattr(current_default, "is_default", False)
      
    
    # Set new default
    setattr(provider, "is_default", True)
    db.commit()
    db.refresh(provider)
    return provider

def update_provider(db: Session, provider: models.Provider, provider_update: schemas.ProviderUpdate):

    update_data = provider_update.model_dump(exclude_unset=True)
    logger.info(f"Updating provider {provider.name} with data: {update_data}")
    for key, value in update_data.items():
        setattr(provider, key, value)
    db.commit()
    db.refresh(provider)
    return provider
    

def delete_provider(db: Session, provider: models.Provider):
    logger.info(f"Deleting provider: {provider.name}")

    db.delete(provider)
    db.commit()
    