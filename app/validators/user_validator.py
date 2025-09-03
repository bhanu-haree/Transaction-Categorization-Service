import re
import logging

from fastapi import HTTPException

from app.models import UserORM

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"
SORT_FIELDS = {"user_id", "name", "email", "created_at"}
SORT_DIRECTIONS = {"asc", "desc"}

logger = logging.getLogger(__name__)

def validate_user_id(user_id: str):
    if not user_id:
        logger.error("user_id is required but missing")
        raise HTTPException(status_code=422, detail="user_id is required")

def validate_limit_offset(limit: int, offset: int):
    if limit < 1 or limit > 200:
        logger.error(f"Invalid limit: {limit}")
        raise HTTPException(status_code=422, detail="limit must be between 1 and 200")
    if offset < 0:
        logger.error(f"Invalid offset: {offset}")
        raise HTTPException(status_code=422, detail="offset must be >= 0")

def validate_sort(sort: str):
    sort_field, _, sort_dir = sort.partition(":")
    if sort_field not in SORT_FIELDS:
        logger.error(f"Invalid sort field: {sort_field}")
        raise HTTPException(status_code=422, detail="Invalid sort field")
    if sort_dir and sort_dir.lower() not in SORT_DIRECTIONS:
        logger.error(f"Invalid sort direction: {sort_dir}")
        raise HTTPException(status_code=422, detail="Invalid sort direction")
    return sort_field, sort_dir or "asc"

def validate_user_create(payload, db):
    if not payload.user_id or not payload.name or not payload.email:
        logger.error("Missing required user fields")
        raise HTTPException(status_code=422, detail="user_id, name, and email are required")
    if not re.match(EMAIL_REGEX, str(payload.email)):
        logger.error(f"Invalid email format: {payload.email}")
        raise HTTPException(status_code=422, detail="Invalid email format")
    existing_email = db.query(UserORM).filter(UserORM.email == str(payload.email)).first()
    if existing_email and (not hasattr(payload, "user_id") or existing_email.user_id != payload.user_id):
        logger.error(f"Email already exists: {payload.email}")
        raise HTTPException(status_code=409, detail="email already exists")

def validate_user_update(payload, db):
    if not payload.name or not payload.email:
        logger.error("Missing required user fields")
        raise HTTPException(status_code=422, detail="user_id, name, and email are required")
    if not re.match(EMAIL_REGEX, str(payload.email)):
        logger.error(f"Invalid email format: {payload.email}")
        raise HTTPException(status_code=422, detail="Invalid email format")
    existing_email = db.query(UserORM).filter(UserORM.email == str(payload.email)).first()
    if existing_email:
        logger.error(f"Email already exists: {payload.email}")
        raise HTTPException(status_code=409, detail="email already exists")