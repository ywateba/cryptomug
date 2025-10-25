from pydantic import BaseModel
from typing import Dict, Optional, List

# --- Token Schemas ---

class TokenBase(BaseModel):
    id: str
    name: Optional[str] = None
    symbol: Optional[str] = None
    description: Optional[str] = None
    is_enabled: bool = False

class TokenCreate(TokenBase):
    pass

class TokenUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None

class Token(TokenBase):
    class ConfigDict:
        from_attributes = True

# --- Provider Schemas ---

class ProviderBase(BaseModel):
    name: str
    api_url: str
    auth_method: str
    token_mapping: Dict[str, str] = {}
    auth_details: Optional[Dict] = None
    is_default: bool = False

class ProviderCreate(ProviderBase):
    pass

class ProviderUpdate(BaseModel):
    api_url: Optional[str] = None
    auth_method: Optional[str] = None
    token_mapping: Optional[Dict[str, str]] = None
    auth_details: Optional[Dict] = None

class Provider(ProviderBase):
    id: int

    class ConfigDict:
        from_attributes = True