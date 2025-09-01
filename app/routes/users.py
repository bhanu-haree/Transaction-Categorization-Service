from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.db.db import get_db
from ..models import UserORM
from app.schemas.user_schema import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.get(UserORM, payload.user_id)
    if existing:
        raise HTTPException(status_code=409, detail="user_id already exists")
    user = UserORM(
        user_id=payload.user_id,
        name=payload.name,
        email=str(payload.email),
        created_at=datetime.utcnow(),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="email already exists")
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = str(payload.email)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="email already exists")
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.get(UserORM, user_id)
    if not user:
        return
    db.delete(user)
    db.commit()
    return

@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by name (icontains)"),
    email: Optional[str] = Query(None, description="Filter by email (icontains)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: str = Query("created_at:desc", description="field:asc|desc; one of user_id,name,email,created_at"),
):
    q = select(UserORM)
    if name:
        q = q.where(func.lower(UserORM.name).like(f"%{name.lower()}%"))
    if email:
        q = q.where(func.lower(UserORM.email).like(f"%{email.lower()}%"))
    sort_field, _, sort_dir = sort.partition(":")
    sort_dir = sort_dir or "asc"
    field_map = {
        "user_id": UserORM.user_id,
        "name": UserORM.name,
        "email": UserORM.email,
        "created_at": UserORM.created_at,
    }
    col = field_map.get(sort_field, UserORM.created_at)
    if sort_dir.lower() == "desc":
        q = q.order_by(col.desc())
    else:
        q = q.order_by(col.asc())
    q = q.offset(offset).limit(limit)
    rows = db.execute(q).scalars().all()
    return rows