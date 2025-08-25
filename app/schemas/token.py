from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None

class RefreshTokenCreate(BaseModel):
    token: str
    user_id: str
    expires_at: datetime

class RefreshTokenInDB(RefreshTokenCreate):
    id: str
    is_revoked: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
