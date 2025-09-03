import re
import logging

from fastapi import HTTPException
from app.schemas.merchant_schema import MerchantCreate

logger = logging.getLogger(__name__)

def validate_merchant_id(merchant_id: str):
    if not merchant_id or not re.match(r"^[a-zA-Z0-9_-]+$", merchant_id):
        logger.error(f"Invalid merchant_id: {merchant_id}")
        raise HTTPException(status_code=422, detail="Invalid merchant_id")

def validate_merchant_payload(payload: MerchantCreate):
    if not payload.display_name or not payload.merchant_id:
        logger.error(f"Missing required fields in merchant payload: merchant_id={payload.merchant_id}, name={payload.display_name}")
        raise HTTPException(status_code=422, detail="Missing required fields")
    validate_merchant_id(payload.merchant_id)