import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import MerchantORM, TransactionORM
from app.schemas.merchant_schema import MerchantCreate, MerchantUpdate
from app.services.transaction_service import delete_transaction_cascade
from app.validators.merchant_validator import validate_merchant_id, validate_merchant_payload

logger = logging.getLogger(__name__)

def create_merchant_service(payload: MerchantCreate, db: Session):
    logger.info(f"Creating merchant: {payload.merchant_id}")
    validate_merchant_payload(payload)
    if db.get(MerchantORM, payload.merchant_id):
        logger.error(f"Merchant ID already exists: {payload.merchant_id}")
        raise HTTPException(status_code=409, detail="merchant_id already exists")
    merchant = MerchantORM(**payload.dict())
    db.add(merchant)
    try:
        db.commit()
        logger.info(f"Merchant created: {merchant.merchant_id}")
    except SQLAlchemyError:
        db.rollback()
        logger.error(f"SQLAlchemyError on merchant creation: {payload.merchant_id}")
        raise HTTPException(status_code=500, detail="Database error")
    db.refresh(merchant)
    return merchant

def get_merchant_service(merchant_id: str, db: Session):
    logger.info(f"Fetching merchant: {merchant_id}")
    validate_merchant_id(merchant_id)
    merchant = db.get(MerchantORM, merchant_id)
    if not merchant:
        logger.error(f"Merchant not found: {merchant_id}")
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

def update_merchant_service(merchant_id: str, payload: MerchantUpdate, db: Session):
    logger.info(f"Updating merchant: {merchant_id}")
    validate_merchant_id(merchant_id)
    merchant = db.get(MerchantORM, merchant_id)
    if not merchant:
        logger.error(f"Merchant not found for update: {merchant_id}")
        raise HTTPException(status_code=404, detail="Merchant not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(merchant, field, value)
    try:
        db.commit()
        logger.info(f"Merchant updated: {merchant_id}")
    except SQLAlchemyError:
        db.rollback()
        logger.error(f"SQLAlchemyError on merchant update: {merchant_id}")
        raise HTTPException(status_code=500, detail="Database error")
    db.refresh(merchant)
    return merchant

def delete_merchant_service(merchant_id: str, db: Session):
    logger.info(f"Deleting merchant: {merchant_id}")
    validate_merchant_id(merchant_id)
    merchant = db.get(MerchantORM, merchant_id)
    if merchant:
        transactions = db.query(TransactionORM).filter(TransactionORM.merchant_id == merchant_id).all()
        delete_transaction_cascade(db, merchant, transactions)
        logger.info(f"Merchant deleted: {merchant_id}")
    else:
        logger.warning(f"Merchant not found for delete: {merchant_id}")
    return

def list_merchants_service(db: Session, aliases: Optional[str] = None, mccs: Optional[str] = None, limit: int = 50, offset: int = 0):
    logger.info(f"Listing merchants: aliases={aliases}, mcc={mccs}, limit={limit}, offset={offset}")
    query = db.query(MerchantORM)
    if aliases:
        query = query.filter(MerchantORM.aliases.ilike(f"%{aliases}%"))
    if mccs:
        query = query.filter(MerchantORM.typical_mccs == mccs)
    merchants = query.offset(offset).limit(limit).all()
    logger.info(f"Merchants listed: count={len(merchants)}")
    return merchants