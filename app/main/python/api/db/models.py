from sqlalchemy import Column, Integer, String, JSON, Boolean
from api.db.database import Base

class Provider(Base): # type: ignore
    """
    SQLAlchemy model for the 'providers' table.
    """
    __tablename__ = "providers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    api_url = Column(String, nullable=False)
    auth_method = Column(String, nullable=False)
    token_mapping = Column(JSON, nullable=False, default={})
    auth_details = Column(JSON, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False, index=True)

class Token(Base): # type: ignore
    """
    SQLAlchemy model for the 'tokens' table.
    """
    __tablename__ = "tokens"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    symbol = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    is_enabled = Column(Boolean, default=False, nullable=False, index=True)