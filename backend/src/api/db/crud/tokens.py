import logging
from api.db import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from api.core import schemas
from api.db.models import Token




logger = logging.getLogger("CryptoMugAPI")



# --- Token CRUD ---

def get_token(db: Session, token_id: str):
    return db.query(Token).filter_by(id=token_id).first()

def get_tokens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Token).offset(skip).limit(limit).all()


def get_enabled_tokens(db: Session, skip: int = 0, limit: int = 100):
    results = db.query(Token.id).filter_by(is_enabled=True).offset(skip).limit(limit).all()
    return [item[0] for item in results] # Unpack tuples to a list of strings

def create_token(db: Session, token: schemas.TokenCreate):
    # The 'is_enabled' flag from the create schema is respected here.
 
    db_token = Token(**token.dict())
    logger.info(f"Creating new token: {token.id}")
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def update_token(db: Session, db_token: Token, token_update: schemas.TokenUpdate):

    update_data = token_update.dict(exclude_unset=True)
    logger.info(f"Updating token {db_token.id} with data: {update_data}")
    for key, value in update_data.items():
        setattr(db_token, key, value)
    db.commit()
    db.refresh(db_token)
    return db_token

def delete_token(db: Session, db_token: Token):
    logger.info(f"Deleting token: {db_token.id}")
    db.delete(db_token)
    db.commit()

def set_token_enabled_status(db: Session, db_token: Token, enabled: bool):
    """Sets the enabled status of a token."""
    if enabled:
        logger.info(f"Enabling token: {db_token.id}")
    else:
        logger.info(f"Disabling token: {db_token.id}")

    setattr(db_token, "is_enabled", enabled)
    db.commit()
    db.refresh(db_token)
    return db_token