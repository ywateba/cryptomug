from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import logging
from sqlalchemy.exc import IntegrityError


from  api.core import schemas
from  api.db.database import get_db
from  api.db.crud import tokens


router = APIRouter(
    prefix="/tokens",
    tags=["Tokens"],
)

logger = logging.getLogger("CryptoMugAPI")

@router.post("/", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def create_token(token: schemas.TokenCreate, db: Session = Depends(get_db)):
    logger.info(f"Received request to create token: {token.id}")
    db_token = tokens.get_token(db, token_id=token.id)
    if db_token: # Eager check to avoid hitting the DB unnecessarily
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Token with this ID already exists")
    try:
        return tokens.create_token(db=db, token=token)
    except IntegrityError: # Catch race condition
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Token with this ID already exists")

@router.get("/", response_model=List[schemas.Token])
def read_tokens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return tokens.get_tokens(db, skip=skip, limit=limit)

@router.get("/enabled/", response_model=List[schemas.Token])
def read_enabled_tokens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves a list of all tokens that are enabled for requests."""
    return tokens.get_enabled_tokens(db, skip=skip, limit=limit)

@router.get("/{token_id}", response_model=schemas.Token)
def read_token(token_id: str, db: Session = Depends(get_db)):
    db_token = tokens.get_token(db, token_id=token_id)
    if not db_token:
        logger.error(f"Token with id '{token_id}' not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    return db_token

@router.post("/{token_id}/enable", response_model=schemas.Token)
def enable_token(token_id: str, db: Session = Depends(get_db)):
    """Marks a token as enabled for requests."""
    db_token = tokens.get_token(db, token_id=token_id)
    if not db_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    return tokens.set_token_enabled_status(db=db, token=db_token, enabled=True)

@router.post("/{token_id}/disable", response_model=schemas.Token)
def disable_token(token_id: str, db: Session = Depends(get_db)):
    """Marks a token as disabled for requests."""
    db_token = tokens.get_token(db, token_id=token_id)
    if not db_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    return tokens.set_token_enabled_status(db=db, token=db_token, enabled=False)

@router.put("/{token_id}", response_model=schemas.Token)
def update_token(token_id: str, token_update: schemas.TokenUpdate, db: Session = Depends(get_db)):
    db_token = tokens.get_token(db, token_id=token_id)
    if not db_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    return tokens.update_token(db=db, token=db_token, token_update=token_update)

@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_token(token_id: str, db: Session = Depends(get_db)):
    db_token = tokens.get_token(db, token_id=token_id)
    if not db_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found")
    tokens.delete_token(db=db, token=db_token)