from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.models import MerchantORM, TransactionORM
from app.schemas.merchant_schema import MerchantCreate, MerchantUpdate

def create_merchant(payload: MerchantCreate, db: Session):
    if db.get(MerchantORM, payload.merchant_id):
        raise HTTPException(status_code=409, detail="merchant_id already exists")
    merchant = MerchantORM(**payload.dict())
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant

def get_merchant(merchant_id: str, db: Session):
    merchant = db.get(MerchantORM, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

def update_merchant(merchant_id: str, payload: MerchantUpdate, db: Session):
    merchant = db.get(MerchantORM, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(merchant, field, value)
    db.commit()
    db.refresh(merchant)
    return merchant

def delete_merchant(merchant_id: str, db: Session):
    merchant = db.get(MerchantORM, merchant_id)
    if merchant:
        # Delete associated transactions
        transactions = db.query(TransactionORM).filter(TransactionORM.merchant_id == merchant_id).all()
        for transaction in transactions:
            db.delete(transaction)
        db.delete(merchant)
        db.commit()
    return

def list_merchants(
        db: Session,
        alias: Optional[str] = None,
        mcc: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
):
    q = select(MerchantORM)
    if alias:
        q = q.where(func.json_each(MerchantORM.aliases).like(f"%{alias}%"))
    if mcc:
        q = q.where(func.json_each(MerchantORM.typical_mccs).like(f"%{mcc}%"))
    q = q.offset(offset).limit(limit)
    return db.execute(q).scalars().all()