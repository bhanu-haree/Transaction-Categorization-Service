from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import UserORM, TransactionORM
from app.schemas.user_schema import UserCreate, UserUpdate

from app.validators.user_validator import validate_user_id, validate_limit_offset, validate_sort, validate_user

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
SORT_FIELDS = {"user_id", "name", "email", "created_at"}
SORT_DIRECTIONS = {"asc", "desc"}


def create_user(payload: UserCreate, db: Session):
    validate_user(payload)
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
        raise HTTPException(status_code=409, detail="User already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    db.refresh(user)
    return user


def get_user(user_id: str, db: Session):
    validate_user_id(user_id)
    user = db.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user(user_id: str, payload: UserUpdate, db: Session):
    validate_user(payload)
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
        raise HTTPException(status_code=409, detail="User already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    db.refresh(user)
    return user

def delete_user(user_id: str, db: Session):
    validate_user_id(user_id)
    user = db.get(UserORM, user_id)
    if not user:
        return
    transactions = db.query(TransactionORM).filter(TransactionORM.user_id == user_id).all()
    for transaction in transactions:
        db.delete(transaction)
    db.delete(user)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    return

def list_users(
        db: Session,
        name: Optional[str] = None,
        email: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort: str = "created_at:desc",
):
    validate_limit_offset(limit, offset)
    sort_field, sort_dir = validate_sort(sort)
    q = select(UserORM)
    if name:
        q = q.where(func.lower(UserORM.name).like(f"%{name.lower()}%"))
    if email:
        q = q.where(func.lower(UserORM.email).like(f"%{email.lower()}%"))
    field_map = {
        "user_id": UserORM.user_id,
        "name": UserORM.name,
        "email": UserORM.email,
        "created_at": UserORM.created_at,
    }
    col = field_map.get(sort_field, UserORM.created_at)
    q = q.order_by(col.desc() if sort_dir.lower() == "desc" else col.asc())
    q = q.offset(offset).limit(limit)
    rows = db.execute(q).scalars().all()
    return rows