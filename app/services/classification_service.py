from typing import Dict, List

from fastapi import HTTPException
from rapidfuzz import fuzz
from sqlalchemy.orm import Session

from app.models import MerchantORM
from app.schemas.classification_schema import ClassificationRequest, ClassificationResult
from app.taxonomy import MCC_CATEGORY_MAP, REGEX_RULES
import logging

logger = logging.getLogger("ClassificationService-Pipeline")
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

logger = logging.getLogger("ClassificationService-Pipeline")

def pipeline_classify(payload: ClassificationRequest, db: Session):
    try:
        logger.info(f"Classifying transaction {payload.id} (merchant_id={payload.merchant_id}, mcc={payload.mcc})")
        normalized = normalize_description(payload.raw_description)

        candidates: Dict[str, Dict] = {}

        def add_signal(cand_category: str, score: float, cand_reason: str):
            logger.debug(f"Adding signal: category={cand_category}, score={score:.2f}, reason={cand_reason}")
            if cand_category not in candidates:
                candidates[cand_category] = {"score": 0.0, "reasons": []}
            candidates[cand_category]["score"] += score
            candidates[cand_category]["reasons"].append(cand_reason)

        # Merchant lookup
        try:
            merchant = db.get(MerchantORM, payload.merchant_id)
        except Exception as e:
            logger.error(f"Error fetching merchant: {e}")
            raise HTTPException(status_code=500, detail="Error fetching merchant data")

        merchant_matched = False
        if merchant:
            if merchant.default_category and merchant.default_category.lower() in normalized:
                add_signal(
                    merchant.default_category,
                    W_MERCHANT,
                    f"Default category from merchant: {merchant.default_category}"
                )
                merchant_matched = True

            for alias in (merchant.aliases or []):
                if alias.lower() in normalized and not merchant_matched:
                    add_signal(
                        merchant.default_category or "Uncategorized",
                        W_MERCHANT,
                        f"Matched alias '{alias}' → {merchant.display_name}"
                    )
                    merchant_matched = True

        # Semantic similarity
        try:
            all_names = [merchant.display_name] + (merchant.aliases or []) if merchant else []
            match = semantic_similarity(normalized, all_names)
        except Exception as e:
            logger.error(f"Error during semantic similarity check: {e}")
            raise HTTPException(status_code=500, detail="Error during semantic similarity check")

        if match:
            best_alias, sim_score = match
            add_signal(
                merchant.default_category or "Uncategorized",
                sim_score * W_SEMANTIC,
                f"Semantic similarity {sim_score:.2f} with '{best_alias}'"
            )

        # MCC map
        if payload.mcc and payload.mcc in MCC_CATEGORY_MAP:
            try:
                cat = MCC_CATEGORY_MAP[payload.mcc]
                add_signal(cat, W_RULE, f"MCC {payload.mcc} aligns with {cat}")
            except KeyError:
                logger.warning(f"MCC {payload.mcc} not found in MCC_CATEGORY_MAP")

        # Regex rules
        for keyword, category, reason in REGEX_RULES:
            if keyword in normalized:
                add_signal(category, W_RULE, reason)

        # Fallback
        if not candidates:
            logger.warning(f"No strong signals for transaction {payload.id}")
            return ClassificationResult(
                transaction_id=payload.id,
                category="Uncategorized",
                confidence=0.5,
                why=["No strong signals"],
                alternatives=[]
            )

        # Normalization
        max_possible_score = W_MERCHANT + W_SEMANTIC + W_RULE
        for category in candidates:
            candidates[category]["score"] = min(
                candidates[category]["score"], 1.0
            )

        # Re-ranking
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

    except HTTPException as http_exc:
        logger.error(f"HTTP error: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during classification")
