from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    user_id: str = Field(..., examples=["user_42"])
    name: str
    email: EmailStr

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserOut(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True