from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
import logging

from api.core.database import get_db
from api.routers import price_service




router = APIRouter(
    prefix="/prices",
    tags=["Prices"],
)

logger = logging.getLogger("CryptoMugAPI")

@router.post("/fetch", status_code=status.HTTP_200_OK)
def fetch_prices(provider_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Triggers the process to fetch prices for all enabled tokens and store them.
    If provider_id is not specified, the default provider will be used.
    """
    logger.info(f"Received request to fetch prices. Provider ID: {provider_id or 'Default'}")
    try:
        return price_service.fetch_and_store_prices(db, provider_id)
    except ValueError as e:
        logger.error(f"Error during price fetch: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))