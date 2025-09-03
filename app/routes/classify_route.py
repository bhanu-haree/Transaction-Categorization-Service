from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from fastapi import APIRouter, Depends, Body
import json
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.schemas.classification_schema import ClassificationRequest, ClassificationResult
from app.db.db import get_db
from app.services.classification_service import pipeline_classify_service
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

@router.post("/", response_model=ClassificationResult)
def classify_transaction(payload: ClassificationRequest = Body(..., description="Transaction to classify",
   example={
       "id": "txn_123",
       "amount": 100.5,
       "currency": "USD",
       "merchant": "Amazon",
       "posted_at": "2024-06-01T12:00:00Z",
       "category": None
   }),
    db: Session = Depends(get_db)):
        validate_transaction(payload, db, payload.id, TransactionORM)
        return pipeline_classify_service(payload, db)

@router.post("/bulk", response_model=List[ClassificationResult])
def classify_bulk(transactions: List[ClassificationRequest] = Body(
    ...,
    min_items=1,
    max_items=1000,
    description="List of transactions to classify (max 1000)",
    example=[
        {
            "id": "txn_123",
            "amount": 100.5,
            "currency": "USD",
            "merchant": "Amazon",
            "posted_at": "2024-06-01T12:00:00Z",
            "category": None
        },
        {
            "id": "txn_124",
            "amount": 50.0,
            "currency": "USD",
            "merchant": "Starbucks",
            "posted_at": "2024-06-02T09:30:00Z",
            "category": None
        }
    ]
),
db: Session = Depends(get_db)):
    logger.info(f"Received bulk classification request for {len(transactions)} transactions")
    txn_ids = [txn.id for txn in transactions if txn.id]
    # Fetch all relevant transactions in one query
    txns = db.query(TransactionORM).filter(TransactionORM.id.in_(txn_ids)).all()
    txn_map = {txn.id: txn for txn in txns}

    def classify(txn_req: ClassificationRequest):
        # Fill missing fields from db_txn if available
        db_txn = txn_map.get(txn_req.id)
        if db_txn:
            data = txn_req.dict()
            for field, value in data.items():
                if (value is None or value == "") and hasattr(db_txn, field):
                    data[field] = getattr(db_txn, field)
            txn_req = ClassificationRequest(**data)
        return pipeline_classify_service(txn_req, db)

    # Parallel processing
    results = []
    with ThreadPoolExecutor() as executor:
        future_to_txn = {executor.submit(classify, txn): txn for txn in transactions}
        for future in as_completed(future_to_txn):
            results.append(future.result())
    return results

@router.post("/classify/bulk/stream")
def classify_bulk_stream(
        requests: List[ClassificationRequest],
        db: Session = Depends(get_db)
):
    logger.info(f"Received bulk stream classification request for {len(requests)} transactions")

    def result_generator():
        yield "["  # start JSON array
        first = True
        for req in requests:
            try:
                result = pipeline_classify_service(req, db)
                if not first:
                    yield ","  # add comma between objects
                else:
                    first = False
                yield json.dumps(result.model_dump())
            except Exception as e:
                logger.error(f"Error in streaming classify for {req.id}: {e}")
        yield "]"  # end JSON array

    return StreamingResponse(result_generator(), media_type="application/json")