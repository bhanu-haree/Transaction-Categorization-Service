from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from app.db.db import engine, Base, get_db
from app.routes.users import router as users_router
from app.routes.merchants import router as merchants_router
from app.routes.transactions import router as transactions_router
from app.routes.classify import router as classification_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bank Transaction Categorization Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

app.include_router(users_router)
app.include_router(merchants_router)
app.include_router(transactions_router)
app.include_router(classification_router)