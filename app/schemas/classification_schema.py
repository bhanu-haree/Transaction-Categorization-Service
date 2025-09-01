from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

class ClassificationRequest(BaseModel):
    id: str
    user_id: Optional[str] = None
    merchant_id: Optional[str] = None
    posted_at:  Optional[datetime] = None
    amount: Optional[float] = 0
    currency: Optional[str] = None
    raw_description: Optional[str] = None
    mcc: Optional[str] = None
    channel: Optional[str] = None
    geo: Optional[Dict] = {}
    account_id: Optional[str] = None

class AlternativeCategory(BaseModel):
    category: str
    confidence: float

class ClassificationResult(BaseModel):
    transaction_id: str
    category: str
    confidence: float
    why: List[str]
    alternatives: List[AlternativeCategory] = []
