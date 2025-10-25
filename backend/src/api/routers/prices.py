from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
import logging

from api.db.crud import providers
from  api.db.database import get_db
from  api.db import influx_service




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

    if not provider_id:
        provider = providers.get_default_provider(db)
        if not provider:
            raise ValueError("No default provider is set.")

    logger.info(f"Using provider '{provider.name}' to fetch prices.")

    # 2. Get all enabled tokens
    enabled_tokens = providers.get_enabled_tokens(db)
    if enabled_tokens:
        try:
            return influx_service.fetch_prices(provider,enabled_tokens)
        except ValueError as e:
            logger.error(f"Error during price fetch: {str(e)}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    else:
        logger.warning("No enabled tokens found. Nothing to fetch.")
        return {"message": "No enabled tokens found.", "provider": provider.name, "prices_written": 0}
  
   