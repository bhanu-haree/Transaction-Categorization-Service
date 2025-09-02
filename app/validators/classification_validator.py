import logging
from fastapi import HTTPException

logger = logging.getLogger("ClassificationValidator")

def validate_transaction(payload, db, transaction_id, transaction_orm):
    logger.info(f"Validating transaction {transaction_id}")
    errors = []
    try:
        txn = db.get(transaction_orm, transaction_id)
        if not txn:
            logger.warning(f"Transaction not found in DB: {transaction_id}")
            errors.append(f"Txn not found in DB: {transaction_id}")
        else:
            mismatches = [
                f"{field}: request={value}, db={getattr(txn, field, None)}"
                for field, value in payload.dict().items()
                if value not in [None, ""] and value != getattr(txn, field, None)
            ]
            if mismatches:
                logger.info(f"Attribute mismatches for transaction {transaction_id}: {mismatches}")
                errors.extend([f"Attribute mismatch for {m}" for m in mismatches])
        if errors:
            logger.error(f"Validation failed for transaction {transaction_id}: {'; '.join(errors)}")
            raise HTTPException(
                status_code=400,
                detail="; ".join(errors)
            )
        logger.info(f"Validation passed for transaction {transaction_id}")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.exception(f"Unexpected error during validation for transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error during transaction validation"
        )