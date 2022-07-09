from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    api_key: Optional[str]
    api_secret: Optional[str]
    chat_id: Optional[int]


class UserOut(BaseModel):
    id: UUID4
    email: EmailStr
    api_key: Optional[str]
    api_secret: Optional[str]
    chat_id: Optional[str]
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
