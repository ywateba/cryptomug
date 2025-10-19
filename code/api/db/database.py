import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from api.config import DATABASE_URL

logger = logging.getLogger("CryptoMugAPI")

logger.info("Setting up database connection...")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency to get a database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()