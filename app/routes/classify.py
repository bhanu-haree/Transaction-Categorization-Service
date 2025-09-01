from typing import List, Dict

from fastapi import APIRouter, Depends
from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.schemas.classification_schema import ClassificationRequest, ClassificationResult
from app.db.db import get_db
from app.models import MerchantORM
from app.taxonomy import MCC_CATEGORY_MAP, REGEX_RULES
from app.models import TransactionORM
import logging

logger = logging.getLogger("classification")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

router = APIRouter(prefix="/classify", tags=["classification"])

# --- Configurable Weights ---
W_MERCHANT = 0.6
W_SEMANTIC = 0.2
W_RULE = 0.2

# --- Helper: normalization ---
# Just strips and lowercases for now
# TODO: Enhance with more NLP techniques
def normalize_description(raw: str) -> str:
    return raw.lower().replace("*", "").strip()

# --- Semantic similarity check ---
# defaults threshold to 80%, else None
def semantic_similarity(desc: str, candidates: List[str], threshold: float = 0.8):
    """
    Returns (best_match, score) if any candidate exceeds threshold, else None.
    Score normalized to [0,1].
    """
    best = None
    best_score = 0
    for cand in candidates:
        score = fuzz.partial_ratio(desc, cand.lower()) / 100.0
        if score > best_score:
            best_score = score
            best = cand
    if best and best_score >= threshold:
        return best, best_score
    return None

# --- Pipeline Version ---
def pipeline_classify(payload: ClassificationRequest, db: Session):
    logger.info(f"Classifying transaction {payload.id} (merchant_id={payload.merchant_id}, mcc={payload.mcc})")
    normalized = normalize_description(payload.raw_description)

    # Track candidates as {category: {"score": float, "reasons": [str]}}
    candidates: Dict[str, Dict] = {}

    def add_signal(cand_category: str, score: float, cand_reason: str):
        logger.debug(f"Adding signal: category={cand_category}, score={score:.2f}, reason={cand_reason}")
        if cand_category not in candidates:
            candidates[cand_category] = {"score": 0.0, "reasons": []}
        candidates[cand_category]["score"] += score
        candidates[cand_category]["reasons"].append(cand_reason)

    # --- Merchant KB ---
    merchant = db.get(MerchantORM, payload.merchant_id)
    if merchant:
        if merchant.default_category:
            # 0.9 weight for exact merchant match
            add_signal(
                merchant.default_category,
                0.9 * W_MERCHANT,
                f"Default category from merchant: {merchant.default_category}"
            )

        for alias in (merchant.aliases or []):
            if alias.lower() in normalized:
                # 0.95 weight for alias substring match, alias has more weightage than category match
                add_signal(
                    merchant.default_category or "Uncategorized",
                    0.95 * W_MERCHANT,
                    f"Matched alias '{alias}' → {merchant.display_name}"
                )

        # --- Semantic similarity ---
        all_names = [merchant.display_name] + (merchant.aliases or [])
        match = semantic_similarity(normalized, all_names)
        if match:
            best_alias, sim_score = match
            add_signal(
                merchant.default_category or "Uncategorized",
                sim_score * W_SEMANTIC,
                f"Semantic similarity {sim_score:.2f} with '{best_alias}'"
            )
    # --- MCC map ---
    if payload.mcc and payload.mcc in MCC_CATEGORY_MAP:
        cat = MCC_CATEGORY_MAP[payload.mcc]
        add_signal(cat, 0.8 * W_RULE, f"MCC {payload.mcc} aligns with {cat}")

    # --- Regex rules ---
    for keyword, category, reason in REGEX_RULES:
        if keyword in normalized:
            add_signal(category, 0.7 * W_RULE, reason)

    # --- Fallback ---
    if not candidates:
        logger.warning(f"No strong signals for transaction {payload.id}")
        return ClassificationResult(
            transaction_id=payload.id,
            category="Uncategorized",
            confidence=0.5,
            why=["No strong signals"],
            alternatives=[]
        )

    # --- Normalization ---
    max_possible_score = W_MERCHANT + W_SEMANTIC + W_RULE
    for category in candidates:
        candidates[category]["score"] = min(
            candidates[category]["score"] / max_possible_score, 1.0
        )

    # --- Re-ranking ---
    best_cat, best_data = max(candidates.items(), key=lambda kv: kv[1]["score"])
    alternatives = [
        {"category": c, "confidence": round(d["score"], 2)}
        for c, d in candidates.items() if c != best_cat
    ]

    logger.info(f"Transaction {payload.id} classified as '{best_cat}' with confidence {best_data['score']:.2f}")
    return ClassificationResult(
        transaction_id=payload.id,
        category=best_cat,
        confidence=round(best_data["score"], 2),
        why=best_data["reasons"],
        alternatives=alternatives
    )


# --- API Endpoints ---
@router.post("/", response_model=ClassificationResult)
def classify_transaction(payload: ClassificationRequest, db: Session = Depends(get_db)):
    logger.info(f"Received classification request for transaction {payload.id}")
    # Fetch transaction if any field is missing
    missing_fields = [field for field, value in payload.model_dump().items() if value is None or value == ""]
    if missing_fields:
        txn = db.get(TransactionORM, payload.id)
        if not txn:
            # TO-DO If transaction not found, fail it
            return pipeline_classify(payload, db)
        # Fill missing fields from txn
        data = payload.dict()
        for field in missing_fields:
            if hasattr(txn, field):
                data[field] = getattr(txn, field)
        payload = ClassificationRequest(**data)
    return pipeline_classify(payload, db)

@router.post("/bulk", response_model=List[ClassificationResult])
# TODO: Need to add pagination or limit or batch for concurrency
def classify_bulk(transactions: List[ClassificationRequest], db: Session = Depends(get_db)):
    logger.info(f"Received bulk classification request for {len(transactions)} transactions")
    return [pipeline_classify(txn, db) for txn in transactions]
