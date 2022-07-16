from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID4
    email: EmailStr
    scopes: Optional[List]
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPermission(BaseModel):
    user_id: UUID4
    scopes: Optional[List[str]]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
    scopes: List[str] = []
