from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import logging

from api.core import schemas
from api.db.database import get_db
from api.db.crud import providers


router = APIRouter(
    prefix="/providers",
    tags=["Providers"],
)

logger = logging.getLogger("CryptoMugAPI")

@router.post("/", response_model=schemas.Provider, status_code=status.HTTP_201_CREATED)
def create_provider(provider: schemas.ProviderCreate, db: Session = Depends(get_db)):
    logger.info(f"Received request to create provider: {provider.name}")
    db_provider = providers.get_provider_by_name(db, provider_name=provider.name)
    if db_provider:
        logger.warning(f"Provider '{provider.name}' already exists.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Provider with this name already exists")
    return providers.create_provider(db=db, provider=provider)

@router.get("/", response_model=List[schemas.Provider])
def read_providers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return providers.get_providers(db, skip=skip, limit=limit)

@router.get("/default", response_model=schemas.Provider)
def read_default_provider(db: Session = Depends(get_db)):
    """Retrieves the currently configured default provider."""
    default_provider = providers.get_default_provider(db)
    if not default_provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No default provider is set")
    return default_provider

@router.get("/{provider_id}", response_model=schemas.Provider)
def read_provider(provider_id: int, db: Session = Depends(get_db)):
    db_provider = providers.get_provider(db, provider_id=provider_id)
    if not db_provider:
        logger.error(f"Provider with id {provider_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return db_provider

@router.post("/{provider_id}/set-default", response_model=schemas.Provider)
def set_default_provider(provider_id: int, db: Session = Depends(get_db)):
    """Sets a specific provider as the default."""
    logger.info(f"Received request to set provider {provider_id} as default.")
    db_provider = providers.get_provider(db, provider_id=provider_id)
    if not db_provider:
        logger.error(f"Provider with id {provider_id} not found to set as default.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return providers.set_default_provider(db=db, provider=db_provider)


@router.put("/{provider_id}", response_model=schemas.Provider)
def update_provider(provider_id: int, provider_update: schemas.ProviderUpdate, db: Session = Depends(get_db)):
    db_provider = providers.get_provider(db, provider_id=provider_id)
    if not db_provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return providers.update_provider(db=db, db_provider=db_provider, provider_update=provider_update)

@router.delete("/{provider_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(provider_name: str, db: Session = Depends(get_db)):
    db_provider = providers.get_provider_by_name(db, provider_name=provider_name)
    if not db_provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    providers.delete_provider(db=db, provider_name=provider_name)