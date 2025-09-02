from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette import status

from app.db.db import get_db

router = APIRouter(prefix="/merchants", tags=["merchants"])
from app.schemas.merchant_schema import MerchantOut, MerchantCreate, MerchantUpdate
from app.services.merchant_service import (
    create_merchant,
    get_merchant,
    update_merchant,
    delete_merchant,
    list_merchants,
)

@router.post("/", response_model=MerchantOut, status_code=status.HTTP_201_CREATED)
def create_merchant(payload: MerchantCreate, db: Session = Depends(get_db)):
    return create_merchant(payload, db)

@router.get("/{merchant_id}", response_model=MerchantOut)
def get_merchant(merchant_id: str, db: Session = Depends(get_db)):
    return get_merchant(merchant_id, db)

@router.put("/{merchant_id}", response_model=MerchantOut)
def update_merchant(merchant_id: str, payload: MerchantUpdate, db: Session = Depends(get_db)):
    return update_merchant(merchant_id, payload, db)

@router.delete("/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_merchant(merchant_id: str, db: Session = Depends(get_db)):
    return delete_merchant(merchant_id, db)

@router.get("/", response_model=List[MerchantOut])
def list_merchants(
        db: Session = Depends(get_db),
        alias: Optional[str] = Query(None, description="Filter by alias substring"),
        mcc: Optional[str] = Query(None, description="Filter by MCC"),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0)
):
    return list_merchants(db, alias, mcc, limit, offset)