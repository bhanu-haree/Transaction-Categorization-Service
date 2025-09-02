from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.schemas.user_schema import UserCreate, UserUpdate, UserOut
from app.services.user_service import (
    create_user,
    get_user,
    update_user,
    delete_user,
    list_users,
)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return create_user(payload, db)

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    return get_user(user_id, db)

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, payload: UserUpdate, db: Session = Depends(get_db)):
    return update_user(user_id, payload, db)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    return delete_user(user_id, db)

@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    name: Optional[str] = Query(None, description="Filter by name (contains)"),
    email: Optional[str] = Query(None, description="Filter by email (contains)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: str = Query("created_at:desc", description="field:asc|desc; one of user_id,name,email,created_at"),
):
    return list_users(db, name, email, limit, offset, sort)