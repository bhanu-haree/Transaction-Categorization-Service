from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import UserORM, TransactionORM
from app.schemas.user_schema import UserCreate, UserUpdate
from app.services.transaction_service import delete_transaction_cascade

from app.validators.user_validator import validate_user_id, validate_limit_offset, validate_sort, validate_user
import logging

logger = logging.getLogger(__name__)

def create_user_service(payload: UserCreate, db: Session):
    logger.info(f"Creating user: {payload.user_id}")
    validate_user(payload, db)
    existing = db.get(UserORM, payload.user_id)
    if existing:
        logger.warning(f"User ID already exists: {payload.user_id}")
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
        logger.info(f"User created: {user.user_id}")
    except IntegrityError:
        db.rollback()
        logger.error(f"IntegrityError on user creation: {payload.user_id}")
        raise HTTPException(status_code=409, detail="User already exists")
    except SQLAlchemyError:
        db.rollback()
        logger.error(f"SQLAlchemyError on user creation: {payload.user_id}")
        raise HTTPException(status_code=500, detail="Database error")
    db.refresh(user)
    return user

def get_user_service(user_id: str, db: Session):
    logger.info(f"Fetching user: {user_id}")
    validate_user_id(user_id)
    user = db.get(UserORM, user_id)
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

def update_user_service(user_id: str, payload: UserUpdate, db: Session):
    logger.info(f"Updating user: {user_id}")
    validate_user(payload, db)
    user = db.get(UserORM, user_id)
    if not user:
        logger.warning(f"User not found for update: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = str(payload.email)
    try:
        db.commit()
        logger.info(f"User updated: {user_id}")
    except IntegrityError:
        db.rollback()
        logger.error(f"IntegrityError on user update: {user_id}")
        raise HTTPException(status_code=409, detail="User already exists")
    except SQLAlchemyError:
        db.rollback()
        logger.error(f"SQLAlchemyError on user update: {user_id}")
        raise HTTPException(status_code=500, detail="Database error")
    db.refresh(user)
    return user

def delete_user_service(user_id: str, db: Session):
    logger.info(f"Deleting user: {user_id}")
    validate_user_id(user_id)
    user = db.get(UserORM, user_id)
    if not user:
        logger.warning(f"User not found for delete: {user_id}")
        return
    transactions = db.query(TransactionORM).filter(TransactionORM.user_id == user_id).all()
    delete_transaction_cascade(db, user, transactions)
    logger.info(f"User deleted: {user_id}")
    return

def list_users_service(
        db: Session,
        name: Optional[str] = None,
        email: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        sort: str = "created_at:desc",
):
    logger.info(f"Listing users: name={name}, email={email}, limit={limit}, offset={offset}, sort={sort}")
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
    logger.info(f"Users listed: count={len(rows)}")
    return rows