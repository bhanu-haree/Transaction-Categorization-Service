from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional

from app.db.db import get_db
from app.models import MerchantORM
from app.schemas.merchant_schema import MerchantCreate, MerchantUpdate, MerchantOut

router = APIRouter(prefix="/merchants", tags=["merchants"])

@router.post("/", response_model=MerchantOut, status_code=status.HTTP_201_CREATED)
def create_merchant(payload: MerchantCreate, db: Session = Depends(get_db)):
    if db.get(MerchantORM, payload.merchant_id):
        raise HTTPException(status_code=409, detail="merchant_id already exists")
    merchant = MerchantORM(**payload.dict())
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant

@router.get("/{merchant_id}", response_model=MerchantOut)
def get_merchant(merchant_id: str, db: Session = Depends(get_db)):
    merchant = db.get(MerchantORM, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return merchant

@router.put("/{merchant_id}", response_model=MerchantOut)
def update_merchant(merchant_id: str, payload: MerchantUpdate, db: Session = Depends(get_db)):
    merchant = db.get(MerchantORM, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(merchant, field, value)

    db.commit()
    db.refresh(merchant)
    return merchant

@router.delete("/{merchant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_merchant(merchant_id: str, db: Session = Depends(get_db)):
    merchant = db.get(MerchantORM, merchant_id)
    if merchant:
        db.delete(merchant)
        db.commit()
    return

@router.get("/", response_model=List[MerchantOut])
def list_merchants(
        db: Session = Depends(get_db),
        alias: Optional[str] = Query(None, description="Filter by alias substring"),
        mcc: Optional[str] = Query(None, description="Filter by MCC"),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0)
):
    q = select(MerchantORM)
    if alias:
        q = q.where(func.json_each(MerchantORM.aliases).like(f"%{alias}%"))
    if mcc:
        q = q.where(func.json_each(MerchantORM.typical_mccs).like(f"%{mcc}%"))
    q = q.offset(offset).limit(limit)
    return db.execute(q).scalars().all()
