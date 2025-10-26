import logging
from api.db import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
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
    try:
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    except IntegrityError:
        db.rollback()
        logger.warning(f"IntegrityError on creating token '{token.id}'. It likely already exists.")
        raise

def update_token(db: Session, token: models.Token, token_update: schemas.TokenUpdate):

    update_data = token_update.model_dump(exclude_unset=True)
    logger.info(f"Updating token {token.id} with data: {update_data}")
    for key, value in update_data.items():
        setattr(token, key, value)
    db.commit()
    db.refresh(token)
    return token

def delete_token(db: Session, token: models.Token):
    logger.info(f"Deleting token: {token.id}")
    db.delete(token)
    db.commit()
    
    
    

def set_token_enabled_status(db: Session, token: models.Token, enabled: bool):
    """Sets the enabled status of a token."""
    if enabled:
        logger.info(f"Enabling token: {token.id}")
    else:
        logger.info(f"Disabling token: {token.id}")

    setattr(token, "is_enabled", enabled)
    db.commit()
    db.refresh(token)
    return token