from datetime import datetime
from typing import Optional

from fastapi import Depends, Query, APIRouter
from requests import Session

from app.db.db import get_db
from app.schemas.transaction_schema import TransactionOut, TransactionCreate, TransactionUpdate
from app.services.transaction_service import (
    create_transaction_service,
    get_transaction_service,
    update_transaction_service,
    delete_transaction_service,
    list_transactions_service, PaginatedTransactions,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=TransactionOut, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    return create_transaction_service(payload, db)

@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    return get_transaction_service(transaction_id, db)

@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)):
    return update_transaction_service(transaction_id, payload, db)

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    delete_transaction_service(transaction_id, db)

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
    return list_transactions_service(
        db=db,
        user_id=user_id,
        merchant_id=merchant_id,
        category=category,
        date_from=date_from,
        date_to=date_to,
        amount_min=amount_min,
        amount_max=amount_max,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )