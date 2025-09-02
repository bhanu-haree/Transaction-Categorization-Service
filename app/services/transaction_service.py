from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc
from typing import Optional, List
from datetime import datetime

from app.models import TransactionORM, UserORM, MerchantORM
from app.schemas.transaction_schema import TransactionOut, TransactionCreate, TransactionUpdate
from pydantic import BaseModel

class PaginatedTransactions(BaseModel):
    total_count: int
    limit: int
    offset: int
    items: List[TransactionOut]

def create_transaction_service(payload: TransactionCreate, db: Session) -> TransactionOut:
    if db.get(TransactionORM, payload.transaction_id):
        raise HTTPException(status_code=409, detail="transaction_id already exists")
    if not db.get(UserORM, payload.user_id):
        raise HTTPException(status_code=404, detail="user_id does not exist")
    if not db.get(MerchantORM, payload.merchant_id):
        raise HTTPException(status_code=404, detail="merchant_id does not exist")
    transaction = TransactionORM(**payload.dict())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_transaction_service(transaction_id: int, db: Session) -> TransactionOut:
    transaction = db.get(TransactionORM, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

def update_transaction_service(transaction_id: int, payload: TransactionUpdate, db: Session) -> TransactionOut:
    transaction = db.get(TransactionORM, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if payload.user_id and not db.get(UserORM, payload.user_id):
        raise HTTPException(status_code=404, detail="user_id does not exist")
    if payload.merchant_id and not db.get(MerchantORM, payload.merchant_id):
        raise HTTPException(status_code=404, detail="merchant_id does not exist")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction

def delete_transaction_service(transaction_id: int, db: Session):
    transaction = db.get(TransactionORM, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    db.commit()

def list_transactions_service(
        db: Session,
        user_id: Optional[str] = None,
        merchant_id: Optional[str] = None,
        category: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        amount_min: Optional[float] = None,
        amount_max: Optional[float] = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "posted_at",
        sort_order: str = "desc"
) -> PaginatedTransactions:
    if user_id and not db.get(UserORM, user_id):
        raise HTTPException(status_code=404, detail="user_id does not exist")
    if merchant_id and not db.get(MerchantORM, merchant_id):
        raise HTTPException(status_code=404, detail="merchant_id does not exist")
    q = select(TransactionORM)
    count_q = select(func.count(TransactionORM.id))
    if user_id:
        q = q.where(TransactionORM.user_id == user_id)
        count_q = count_q.where(TransactionORM.user_id == user_id)
    if merchant_id:
        q = q.where(TransactionORM.merchant_id == merchant_id)
        count_q = count_q.where(TransactionORM.merchant_id == merchant_id)
    if date_from:
        q = q.where(TransactionORM.posted_at >= date_from)
        count_q = count_q.where(TransactionORM.posted_at >= date_from)
    if date_to:
        q = q.where(TransactionORM.posted_at <= date_to)
        count_q = count_q.where(TransactionORM.posted_at <= date_to)
    if amount_min is not None:
        q = q.where(TransactionORM.amount >= amount_min)
        count_q = count_q.where(TransactionORM.amount >= amount_min)
    if amount_max is not None:
        q = q.where(TransactionORM.amount <= amount_max)
        count_q = count_q.where(TransactionORM.amount <= amount_max)
    sort_col = getattr(TransactionORM, sort_by)
    q = q.order_by(asc(sort_col) if sort_order == "asc" else desc(sort_col))
    total_count = db.execute(count_q).scalar_one()
    q = q.offset(offset).limit(limit)
    items = db.execute(q).scalars().all()
    return PaginatedTransactions(
        total_count=total_count,
        limit=limit,
        offset=offset,
        items=items
    )