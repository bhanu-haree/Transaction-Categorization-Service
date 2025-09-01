from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field

class TransactionCreate(BaseModel):
    id: str = Field(..., examples=["txn_123"])
    user_id: str
    merchant_id: str
    posted_at: datetime
    amount: float
    currency: str
    raw_description: str
    mcc: Optional[str] = None
    channel: Optional[str] = None
    geo: Optional[Dict] = {}
    account_id: Optional[str] = None

class TransactionUpdate(BaseModel):
    posted_at: Optional[datetime] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    raw_description: Optional[str] = None
    mcc: Optional[str] = None
    channel: Optional[str] = None
    geo: Optional[Dict] = None
    account_id: Optional[str] = None

class TransactionOut(BaseModel):
    id: str
    user_id: str
    merchant_id: str
    posted_at: datetime
    amount: float
    currency: str
    raw_description: str
    normalized_description: Optional[str]
    mcc: Optional[str]
    channel: Optional[str]
    geo: Dict
    account_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
