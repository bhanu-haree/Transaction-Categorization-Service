from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from starlette import status
from typing import List, Optional

from app.db.db import get_db
from app.schemas.merchant_schema import MerchantOut, MerchantCreate, MerchantUpdate
from app.services.merchant_service import (
    create_merchant_service,
    get_merchant_service,
    update_merchant_service,
    delete_merchant_service,
    list_merchants_service,
)

router = APIRouter(prefix="/merchants", tags=["merchants"])

@router.post("/", response_model=MerchantOut, status_code=status.HTTP_201_CREATED)
def create_merchant(
        payload: MerchantCreate,
        db: Session = Depends(get_db)
):
    return create_merchant_service(payload, db)

@router.put("/{merchant_id}", response_model=MerchantOut)
def update_merchant(
        payload: MerchantUpdate,
        merchant_id: str = Path(..., min_length=1, max_length=64, regex="^[a-zA-Z0-9_-]+$", description="Merchant ID"),
        db: Session = Depends(get_db)
):
    return update_merchant_service(merchant_id, payload, db)

@router.get("/{merchant_id}", response_model=MerchantOut)
def get_merchant(
        merchant_id: str = Path(..., min_length=1, max_length=64, regex="^[a-zA-Z0-9_-]+$", description="Merchant ID"),
        db: Session = Depends(get_db)
):
    return get_merchant_service(merchant_id, db)

@router.delete("/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_merchant(
        merchant_id: str = Path(..., min_length=1, max_length=64, regex="^[a-zA-Z0-9_-]+$", description="Merchant ID"),
        db: Session = Depends(get_db)
):
    return delete_merchant_service(merchant_id, db)

@router.get("/", response_model=List[MerchantOut])
def list_merchants(
        db: Session = Depends(get_db),
        alias: Optional[str] = Query(None, min_length=1, max_length=64, description="Filter by alias substring"),
        mcc: Optional[str] = Query(None, min_length=3, max_length=4, regex="^[0-9]+$", description="Filter by MCC"),
        limit: int = Query(50, ge=1, le=200, description="Max number of merchants to return"),
        offset: int = Query(0, ge=0, description="Offset for pagination")
):
    return list_merchants_service(db, alias, mcc, limit, offset)