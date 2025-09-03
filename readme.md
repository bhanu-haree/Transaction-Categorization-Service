# Bank Transaction Categorization Service

A FastAPI-based microservice for automatic categorization of bank transactions using merchant knowledge base, MCC codes, regex rules, and semantic similarity.

## Features

- Transaction classification via `/classify` and `/classify/bulk`
- Merchant, MCC, and regex-based enrichment
- Weighted scoring and explainable output
- Bulk and streaming classification for high throughput
- CRUD APIs for users, merchants, and transactions

## API Endpoints

- `POST /classify` — Classify a single transaction
- `POST /classify/bulk` — Classify multiple transactions in parallel (batch mode)
- `POST /classify/bulk/stream` — Stream classification results for large batches
- `GET /transactions` — List transactions (filter, sort, paginate)
- `POST /transactions` — Create a transaction
- `GET /merchants` — List merchants (filter, paginate)
- `POST /merchants` — Create a merchant
- `GET /users` — List users (filter, paginate)
- `POST /users` — Create a user
- `GET /health` — Health check

## Quickstart

1. **Clone the repo:**
   ```bash
   git clone https://github.com/<your-username>/Transaction-Categorization-Service.git
   cd Transaction-Categorization-Service
   ```
2. **Create a virtualenvironment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ``` 
   
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Open API docs:**  
   Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

6. **DB is pre-loaded with sample data.** 
    If more data is needed, need to call `POST /transaction`,`POST /merchants` and `POST /users` endpoints.
---

## 🗺️ Classification Flow

```mermaid
flowchart TD
    A[Start: Transaction Input] --> B[Normalize Description]
    B --> C{Merchant Found?}
    
    C -- Yes --> D[Check Default Category / Aliases]
    C -- No --> E[Skip Merchant Match]

    D --> F[Semantic Similarity (Merchant Names + Aliases)]
    E --> F

    F --> G{MCC Present?}
    G -- Yes --> H[Map MCC → Category]
    G -- No --> I[Skip MCC]

    H --> J[Regex Rules Matching]
    I --> J

    J --> K{Any Signals Collected?}
    K -- No --> L[Category = Uncategorized | Confidence=0.5]
    K -- Yes --> M[Normalize Scores (0.0 - 1.0)]

    M --> N[Pick Best Category]
    N --> O[Rank Alternatives]
    O --> P[Return Classification Result ✅]

----> Q[End]
```

## 📂 Example Requests

### 🔹 Single Transaction Classification
**Request**
```http
POST /classify
Content-Type: application/json

{
    "id": "txn_test_multi3",
    "user_id": "user_42",
    "merchant_id": "m_store",
    "amount": 45.00,
    "currency": "USD",
    "raw_description": "WALMART STARBUCKS MONTHLY FEE CHARGE",
    "mcc": "5399"
  }
```

---

### 🔹 Bulk Classification (Batch Mode)
**Request**
```http
POST /classify/bulk
Content-Type: application/json

[
  {
    "id": "txn_test_multi3",
    "user_id": "user_42",
    "merchant_id": "m_store",
    "amount": 45.00,
    "currency": "USD",
    "raw_description": "WALMART STARBUCKS MONTHLY FEE CHARGE",
    "mcc": "5399"
  },
  {
    "id": "txn_test_multi4",
    "user_id": "user_42",
    "merchant_id": "m_store",
    "amount": 45.00,
    "currency": "USD",
    "raw_description": "WALMART STARBUCKS UBER MONTHLY FEE",
    "mcc": "5812"
  }
]
```

**Response**
```json
[
  {
    "transaction_id": "txn_test_multi3",
    "category": "Fees & Charges > Bank Fee",
    "confidence": 0.4,
    "why": ["Regex rule: 'monthly fee'", "Regex rule: 'charge'"],
    "alternatives": [
      {"category": "Food & Drink > Coffee Shop", "confidence": 0.2},
      {"category": "Shopping > General Retail", "confidence": 0.2}
    ]
  },
  {
    "transaction_id": "txn_test_multi4",
    "category": "Food & Drink > Restaurant",
    "confidence": 0.2,
    "why": ["MCC 5812 aligns with Food & Drink > Restaurant"],
    "alternatives": [
      {"category": "Transport > Rideshare", "confidence": 0.2},
      {"category": "Food & Drink > Coffee Shop", "confidence": 0.2},
      {"category": "Shopping > General Retail", "confidence": 0.2},
      {"category": "Fees & Charges > Bank Fee", "confidence": 0.2}
    ]
  }
]
```

---

### 🔹 Bulk Classification (Streaming Mode)
**Request**
```http
POST /classify/bulk/stream
Content-Type: application/json

[
  {
    "id": "txn_test_multi3",
    "user_id": "user_42",
    "merchant_id": "m_store",
    "amount": 45.00,
    "currency": "USD",
    "raw_description": "WALMART STARBUCKS MONTHLY FEE CHARGE",
    "mcc": "5399"
  },
  {
    "id": "txn_test_multi4",
    "user_id": "user_42",
    "merchant_id": "m_store",
    "amount": 45.00,
    "currency": "USD",
    "raw_description": "WALMART STARBUCKS UBER MONTHLY FEE",
    "mcc": "5812"
  }
]
```

**Response (NDJSON stream)**
```json
{"transaction_id": "txn_test_multi3", "category": "Fees & Charges > Bank Fee", "confidence": 0.4, "why": ["Regex rule: 'monthly fee'", "Regex rule: 'charge'"], "alternatives": [{"category": "Food & Drink > Coffee Shop", "confidence": 0.2}, {"category": "Shopping > General Retail", "confidence": 0.2}]}
{"transaction_id": "txn_test_multi4", "category": "Food & Drink > Restaurant", "confidence": 0.2, "why": ["MCC 5812 aligns with Food & Drink > Restaurant"], "alternatives": [{"category": "Transport > Rideshare", "confidence": 0.2}, {"category": "Food & Drink > Coffee Shop", "confidence": 0.2}, {"category": "Shopping > General Retail", "confidence": 0.2}, {"category": "Fees & Charges > Bank Fee", "confidence": 0.2}]}
```

---

## 🚀 Scaling Notes

- **Batch mode** (`/bulk`) for smaller payloads (≤ 1k txns).
- **Streaming mode** (`/bulk/stream`) for very large inputs (100k+ txns).
- SQLAlchemy bulk `in_` query prevents N+1 lookups.
- Parallel classification using `concurrent.futures` for CPU-bound tasks.
- Observability with latency, throughput, error rate metrics.

---

