from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class MerchantCreate(BaseModel):
    merchant_id: str = Field(..., examples=["m_amazon"])
    display_name: str
    aliases: Optional[List[str]] = []
    typical_mccs: Optional[List[str]] = []
    default_category: Optional[str] = None

class MerchantUpdate(BaseModel):
    display_name: Optional[str] = None
    aliases: Optional[List[str]] = None
    typical_mccs: Optional[List[str]] = None
    default_category: Optional[str] = None

class MerchantOut(BaseModel):
    merchant_id: str
    display_name: str
    aliases: List[str] = []
    typical_mccs: List[str] = []
    default_category: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
