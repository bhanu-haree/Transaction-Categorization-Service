from concurrent.futures import ThreadPoolExecutor, as_completed
from select import select
from typing import List

from fastapi import APIRouter, Depends
from pydantic import json
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.schemas.classification_schema import ClassificationRequest, ClassificationResult
from app.db.db import get_db
from app.services.classification_service import pipeline_classify
from app.models import TransactionORM
from app.validators.classification_validator import validate_transaction
import logging

logger = logging.getLogger("classification")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

router = APIRouter(prefix="/classify", tags=["classification"])

# --- API Endpoints ---
@router.post("/", response_model=ClassificationResult)
def classify_transaction(payload: ClassificationRequest, db: Session = Depends(get_db)):
    validate_transaction(payload, db, payload.id, TransactionORM)
    return pipeline_classify(payload, db)

@router.post("/bulk", response_model=List[ClassificationResult])
def classify_bulk(transactions: List[ClassificationRequest], db: Session = Depends(get_db)):
    logger.info(f"Received bulk classification request for {len(transactions)} transactions")
    txn_ids = [txn.id for txn in transactions if txn.id]
    # Fetch all relevant transactions in one query
    db_txns = db.execute(
        select(TransactionORM).where(TransactionORM.id.in_(txn_ids))
    ).scalars().all()
    txn_map = {txn.id: txn for txn in db_txns}

    def classify(txn_req: ClassificationRequest):
        # Fill missing fields from db_txn if available
        db_txn = txn_map.get(txn_req.id)
        if db_txn:
            data = txn_req.dict()
            for field, value in data.items():
                if (value is None or value == "") and hasattr(db_txn, field):
                    data[field] = getattr(db_txn, field)
            txn_req = ClassificationRequest(**data)
        return pipeline_classify(txn_req, db)

    # Parallel processing
    results = []
    with ThreadPoolExecutor() as executor:
        future_to_txn = {executor.submit(classify, txn): txn for txn in transactions}
        for future in as_completed(future_to_txn):
            results.append(future.result())
    return results

@router.post("/bulk/stream")
def classify_bulk_stream(transactions: List[ClassificationRequest], db: Session = Depends(get_db)):
    logger.info(f"Received bulk stream classification request for {len(transactions)} transactions")
    txn_ids = [txn.id for txn in transactions if txn.id]
    db_txns = db.execute(
        select(TransactionORM).where(TransactionORM.id.in_(txn_ids))
    ).scalars().all()
    txn_map = {txn.id: txn for txn in db_txns}

    def classify(txn_req: ClassificationRequest):
        db_txn = txn_map.get(txn_req.id)
        if db_txn:
            data = txn_req.dict()
            for field, value in data.items():
                if (value is None or value == "") and hasattr(db_txn, field):
                    data[field] = getattr(db_txn, field)
            txn_req = ClassificationRequest(**data)
        return pipeline_classify(txn_req, db)

    def result_generator():
        with ThreadPoolExecutor() as executor:
            future_to_txn = {executor.submit(classify, txn): txn for txn in transactions}
            for future in as_completed(future_to_txn):
                result = future.result()
                yield json.dumps(result.model_dump()) + "\n"

    return StreamingResponse(result_generator(), media_type="application/json")