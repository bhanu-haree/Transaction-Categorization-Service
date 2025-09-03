from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Path, status, Body
from sqlalchemy.orm import Session

from app.db.db import get_db
from app.schemas.user_schema import UserCreate, UserUpdate, UserOut
from app.services.user_service import (
    create_user_service,
    get_user_service,
    update_user_service,
    delete_user_service,
    list_users_service,
)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
        payload: UserCreate = Body(..., example={
            # -- This should be matching with TXN in DB
            "user_id": "u_123",
            "name": "John Doe",
            "email": "john@example.com",
            "password": "strongpassword123"
        }),
        db: Session = Depends(get_db)
):
    return create_user_service(payload, db)

@router.get("/{user_id}", response_model=UserOut)
def get_user(
        user_id: str = Path(..., min_length=1, max_length=64, regex="^[a-zA-Z0-9_-]+$", description="User ID"),
        db: Session = Depends(get_db)
):
    return get_user_service(user_id, db)

@router.put("/{user_id}", response_model=UserOut)
def update_user(
        user_id: str = Path(..., min_length=1, max_length=64, regex="^[a-zA-Z0-9_-]+$", description="User ID"),
        payload: UserUpdate = Body(...),
        db: Session = Depends(get_db)
):
    return update_user_service(user_id, payload, db)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str = Path(
            ...,
            min_length=3,
            max_length=64,
            regex="^[a-zA-Z0-9_-]+$",
            description="Unique user ID to delete"
        ),
        db: Session = Depends(get_db)
):
    return delete_user_service(user_id, db)

@router.get("/", response_model=List[UserOut])
def list_users(
        db: Session = Depends(get_db),
        name: Optional[str] = Query(None, min_length=1, max_length=128, description="Filter by name (contains)"),
        email: Optional[str] = Query(None, min_length=5, max_length=128, description="Filter by email (contains)"),
        limit: int = Query(50, ge=1, le=200, description="Max number of users to return"),
        offset: int = Query(0, ge=0, description="Offset for pagination"),
        sort: str = Query("created_at:desc", description="field:asc|desc; one of user_id,name,email,created_at"),
):
    return list_users_service(db, name, email, limit, offset, sort)