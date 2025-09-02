import re

from fastapi import HTTPException

from app.services.user_service import EMAIL_REGEX, SORT_FIELDS, SORT_DIRECTIONS

def validate_user_id(user_id: str):
    if not user_id:
        raise HTTPException(status_code=422, detail="user_id is required")


def validate_limit_offset(limit: int, offset: int):
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=422, detail="limit must be between 1 and 200")
    if offset < 0:
        raise HTTPException(status_code=422, detail="offset must be >= 0")


def validate_sort(sort: str):
    sort_field, _, sort_dir = sort.partition(":")
    if sort_field not in SORT_FIELDS:
        raise HTTPException(status_code=422, detail="Invalid sort field")
    if sort_dir and sort_dir.lower() not in SORT_DIRECTIONS:
        raise HTTPException(status_code=422, detail="Invalid sort direction")
    return sort_field, sort_dir or "asc"


def validate_user(payload):
    if not payload.user_id or not payload.name or not payload.email:
        raise HTTPException(status_code=422, detail="user_id, name, and email are required")
    if not re.match(EMAIL_REGEX, str(payload.email)):
        raise HTTPException(status_code=422, detail="Invalid email format")
