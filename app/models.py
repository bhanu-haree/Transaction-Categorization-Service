from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Float
from datetime import datetime

from app.db.db import Base


class UserORM(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

class MerchantORM(Base):
    __tablename__ = "merchants"
    merchant_id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=False)
    aliases = Column(JSON, default=list)       # list of strings
    typical_mccs = Column(JSON, default=list)  # list of MCCs
    default_category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class TransactionORM(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    merchant_id = Column(String, ForeignKey("merchants.merchant_id"), nullable=False)
    posted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    raw_description = Column(String, nullable=False)
    normalized_description = Column(String, nullable=True)
    mcc = Column(String, nullable=True)
    channel = Column(String, nullable=True)  # e.g. pos, ecom, atm
    geo = Column(JSON, default=dict)
    account_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)