## Transaction Categorization Service

A Python-based Service for automatic categorization of transactions using merchant data, semantic matching, and rule-based signals.

### Features

- **Transaction Classification**: Assigns categories to transactions based on merchant info, MCC codes, and regex rules.
- **Bulk Classification**: Efficiently processes large batches of transactions.
- **User, Merchant & Transaction Management**: CRUD endpoints for users, merchants and transactions.
- **Extensible**: Easily add new rules, merchants, or categories.
- **Taxonomy Support**: Hierarchical category structure for detailed classification. Ideally this should be a learning module from the Transaction/Classification data

### Tech Stack

- **Python 3.12**
- **FastAPI** (API framework)
- **SQLAlchemy** (ORM)
- **SQLite** (default DB, see `app.db`)
- **Uvicorn** (ASGI server)

### Directory Structure

- `app/`
    - `main.py`: FastAPI app entry point
    - `models.py`: ORM models
    - `taxonomy.py`: Category taxonomy logic
    - `db/`: DB setup and seed data
    - `routes/`: API endpoints (`classify.py`, `merchants.py`, etc.)
    - `schemas/`: Pydantic schemas for request/response validation

### Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run DB seed (optional)**
   ```bash
   python app/db/seed_data.py
   ```

3. **Start the API server**
   ```bash
   uvicorn app.main:app --reload
   ```

### Usage

- **Classify a transaction**:  
  `POST /classify/` with transaction details.
- **Bulk classification**:  
  `POST /classify/bulk` with a list of transactions in sync manner.
- **Bulk stream classification**:  
    `POST /classify/bulk/stream` streams the classification results as they are processed in async manner.
- **Manage merchants/categories**:  
  Use endpoints in `routes/merchants.py` and `routes/users.py`.

### OpenAPI & Interactive Docs
- OpenAPI Spec: All endpoints are automatically documented using OpenAPI (Swagger) via FastAPI.
- Interactive Documentation:
- Access Swagger UI at http://127.0.0.1:8000/docs#/
- Usage:
- Explore, test, and view request/response schemas directly in the browser.
- OpenAPI spec is available at /openapi.json for integration and tooling.

### Configuration

- **Weights & Multipliers**:  
  Fine-tune classification by adjusting parameters in `routes/classify.py`.
- **Logging**:  
  Logs are output to console; configure in `routes/classify.py`.

### License

For educational/demo use only. See assignment PDF for details.

---