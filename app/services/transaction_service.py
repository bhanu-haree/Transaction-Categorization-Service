import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from datetime import datetime

from app.models import TransactionORM, UserORM, MerchantORM
from app.schemas.transaction_schema import TransactionOut, TransactionCreate, TransactionUpdate
from pydantic import BaseModel

from app.validators.transaction_validator import validate_transaction_create, validate_transaction_update

logger = logging.getLogger(__name__)

class PaginatedTransactions(BaseModel):
    total_count: int
    limit: int
    offset: int
    items: List[TransactionOut]

def create_transaction_service(payload: TransactionCreate, db: Session) -> TransactionOut:
    logger.info(f"Creating transaction: {payload.transaction_id}")
    validate_transaction_create(db, payload)
    transaction = TransactionORM(**payload.dict())
    db.add(transaction)
    try:
        db.commit()
        logger.info(f"Transaction created: {transaction.transaction_id}")
    except SQLAlchemyError:
        db.rollback()
        logger.error(f"Database error during transaction creation: {payload.transaction_id}")
        raise HTTPException(status_code=500, detail="Database error during creation")
    db.refresh(transaction)
    return transaction


def get_transaction_service(transaction_id: int, db: Session) -> TransactionOut:
    logger.info(f"Fetching transaction: {transaction_id}")
    transaction = db.get(TransactionORM, transaction_id)
    if not transaction:
        logger.warning(f"Transaction not found: {transaction_id}")
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

def update_transaction_service(transaction_id: int, payload: TransactionUpdate, db: Session) -> TransactionOut:
    logger.info(f"Updating transaction: {transaction_id}")
    transaction = db.get(TransactionORM, transaction_id)
    validate_transaction_update(db, payload, transaction, transaction_id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(transaction, field, value)
    try:
        db.commit()
        logger.info(f"Transaction updated: {transaction_id}")
    except SQLAlchemyError:
        db.rollback()
        logger.error(f"Database error during transaction update: {transaction_id}")
        raise HTTPException(status_code=500, detail="Database error during update")
    db.refresh(transaction)
    return transaction


def delete_transaction_service(transaction_id: int, db: Session):
    logger.info(f"Deleting transaction: {transaction_id}")
    transaction = db.get(TransactionORM, transaction_id)
    if not transaction:
        logger.warning(f"Transaction not found for delete: {transaction_id}")
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    try:
        db.commit()
        logger.info(f"Transaction deleted: {transaction_id}")
    except SQLAlchemyError:
        db.rollback()
        logger.error(f"Database error during transaction delete: {transaction_id}")
        raise HTTPException(status_code=500, detail="Database error during delete")

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
    logger.info(f"Listing transactions: user_id={user_id}, merchant_id={merchant_id}, category={category}, "
                f"date_from={date_from}, date_to={date_to}, amount_min={amount_min}, amount_max={amount_max}, "
                f"limit={limit}, offset={offset}, sort_by={sort_by}, sort_order={sort_order}")
    if user_id and not db.get(UserORM, user_id):
        logger.warning(f"user_id does not exist for listing: {user_id}")
        raise HTTPException(status_code=404, detail="user_id does not exist")
    if merchant_id and not db.get(MerchantORM, merchant_id):
        logger.warning(f"merchant_id does not exist for listing: {merchant_id}")
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
    logger.info(f"Transactions listed: count={len(items)}")
    return PaginatedTransactions(
        total_count=total_count,
        limit=limit,
        offset=offset,
        items=items
    )

def delete_transaction_cascade(db, merchant, transactions):
    logger.info(f"Deleting entity and cascading transactions: transaction_count={len(transactions)}")
    for transaction in transactions:
        db.delete(transaction)
    db.delete(merchant)
    try:
        db.commit()
        logger.info(f"Entity and related transactions deleted")
    except SQLAlchemyError:
        db.rollback()
        logger.error(f"Database error during merchant cascade delete")
        raise HTTPException(status_code=500, detail="Database error")