from fastapi import HTTPException

from app.models import TransactionORM, UserORM, MerchantORM
import logging

logger = logging.getLogger(__name__)

def validate_transaction_create(db, payload):
    if db.get(TransactionORM, payload.id):
        logger.warning(f"Transaction ID already exists: {payload.id}")
        raise HTTPException(status_code=409, detail="transaction_id already exists")
    if not db.get(UserORM, payload.user_id):
        logger.warning(f"user_id does not exist: {payload.user_id}")
        raise HTTPException(status_code=404, detail="user_id does not exist")
    if not db.get(MerchantORM, payload.merchant_id):
        logger.warning(f"merchant_id does not exist: {payload.merchant_id}")
        raise HTTPException(status_code=404, detail="merchant_id does not exist")


def validate_transaction_update(db, payload, transaction, transaction_id):
    if not transaction:
        logger.warning(f"Transaction not found for update: {transaction_id}")
        raise HTTPException(status_code=404, detail="Transaction not found")
    if payload.user_id and not db.get(UserORM, payload.user_id):
        logger.warning(f"user_id does not exist for update: {payload.user_id}")
        raise HTTPException(status_code=404, detail="user_id does not exist")
    if payload.merchant_id and not db.get(MerchantORM, payload.merchant_id):
        logger.warning(f"merchant_id does not exist for update: {payload.merchant_id}")
        raise HTTPException(status_code=404, detail="merchant_id does not exist")
