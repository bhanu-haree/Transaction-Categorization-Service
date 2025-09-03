from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    user_id: str = Field(
        ...,
        min_length=3,
        max_length=64,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Unique user ID"
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=128,
        description="Full name of the user"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be 8-128 characters long, include at least one letter and one number"
    )
    @validator("password")
    def password_complexity(cls, v):
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must include at least one letter and one number")
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=128,
        description="Full name of the user"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Valid email address"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="Password must be 8-128 characters long, include at least one letter and one number"
    )
    @validator("password")
    def password_complexity(cls, v):
        if v is not None and (not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v)):
            raise ValueError("Password must include at least one letter and one number")
        return v


class UserOut(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True