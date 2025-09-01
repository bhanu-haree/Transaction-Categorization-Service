from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc
from typing import List, Optional
from datetime import datetime

from app.db.db import get_db
from app.models import TransactionORM
from app.schemas.transaction_schema import TransactionOut

from pydantic import BaseModel

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Response wrapper for pagination
class PaginatedTransactions(BaseModel):
    total_count: int
    limit: int
    offset: int
    items: List[TransactionOut]

@router.get("/", response_model=PaginatedTransactions)
def list_transactions(
        db: Session = Depends(get_db),
        user_id: Optional[str] = Query(None),
        merchant_id: Optional[str] = Query(None),
        category: Optional[str] = Query(None),
        date_from: Optional[datetime] = Query(None),
        date_to: Optional[datetime] = Query(None),
        amount_min: Optional[float] = Query(None),
        amount_max: Optional[float] = Query(None),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        sort_by: str = Query("posted_at", regex="^(posted_at|amount|created_at)$"),
        sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """
    List transactions with filters, pagination, and sorting.
    Returns metadata (total_count, limit, offset) and results.
    """

    q = select(TransactionORM)
    count_q = select(func.count(TransactionORM.id))

    # Apply filters
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

    # Sorting
    sort_col = getattr(TransactionORM, sort_by)
    q = q.order_by(asc(sort_col) if sort_order == "asc" else desc(sort_col))

    # Total count before pagination
    total_count = db.execute(count_q).scalar_one()

    # Pagination
    q = q.offset(offset).limit(limit)

    items = db.execute(q).scalars().all()

    return PaginatedTransactions(
        total_count=total_count,
        limit=limit,
        offset=offset,
        items=items
    )
