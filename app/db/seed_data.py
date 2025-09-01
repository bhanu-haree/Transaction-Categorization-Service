import json
from datetime import datetime

from sqlalchemy.orm import Session

import app.models as models
from db import SessionLocal, engine

#  Ensure tables are created
models.Base.metadata.create_all(bind=engine)

# Sample merchants
MERCHANTS = [
    {
        "merchant_id": "m_amazon",
        "display_name": "Amazon",
        "aliases": ["AMZN", "Amazon Mktp", "AMAZON.COM"],
        "typical_mccs": ["5942", "4899"],
        "default_category": "Shopping > Online Marketplace",
    },
    {
        "merchant_id": "m_starbucks",
        "display_name": "Starbucks",
        "aliases": ["STARBUCKS", "SBX", "STARBUCKS STORE"],
        "typical_mccs": ["5814", "5811"],
        "default_category": "Food & Drink > Coffee Shop",
    },
    {
        "merchant_id": "m_uber",
        "display_name": "Uber",
        "aliases": ["UBER", "UBER TRIP"],
        "typical_mccs": ["4121"],
        "default_category": "Transport > Rideshare",
    },
    {
        "merchant_id": "m_mcd",
        "display_name": "McDonalds",
        "aliases": ["MCDONALDS", "MCD"],
        "typical_mccs": ["5814"],
        "default_category": "Food & Drink > Fast Food",
    },
    {
        "merchant_id": "m_netflix",
        "display_name": "Netflix",
        "aliases": ["NETFLIX"],
        "typical_mccs": ["7841", "4899"],
        "default_category": "Subscriptions > Streaming",
    },
    {
        "merchant_id": "m_airbnb",
        "display_name": "Airbnb",
        "aliases": ["AIRBNB"],
        "typical_mccs": ["6513"],
        "default_category": "Travel > Short-term Rental",
    },
    {
        "merchant_id": "m_cvs",
        "display_name": "CVS Pharmacy",
        "aliases": ["CVS", "CVS PHARMACY"],
        "typical_mccs": ["5912"],
        "default_category": "Healthcare > Pharmacy",
    },
    {
        "merchant_id": "m_att",
        "display_name": "AT&T",
        "aliases": ["AT&T", "ATT WIRELESS"],
        "typical_mccs": ["4814"],
        "default_category": "Bills & Utilities > Internet/Mobile",
    },
]

# Sample transactions
TRANSACTIONS = [
    {"id": "t1", "raw_description": "AMZN Mktp purchase", "amount": 120.50, "mcc": "5942"},
    {"id": "t2", "raw_description": "STARBUCKS STORE #123", "amount": 6.75, "mcc": "5811"},
    {"id": "t3", "raw_description": "UBER*TRIP 987654", "amount": 18.20, "mcc": "4121"},
    {"id": "t4", "raw_description": "MCDONALDS #5555", "amount": 9.99, "mcc": "5814"},
    {"id": "t5", "raw_description": "NETFLIX.COM Monthly Subscription", "amount": 15.49, "mcc": "7841"},
    {"id": "t6", "raw_description": "AIRBNB PAYMENTS PARIS", "amount": 250.00, "mcc": "6513"},
    {"id": "t7", "raw_description": "CVS PHARMACY #1200", "amount": 32.40, "mcc": "5912"},
    {"id": "t8", "raw_description": "AT&T Wireless Bill", "amount": 89.99, "mcc": "4814"},
    {"id": "t9", "raw_description": "ATM Withdrawal - NYC", "amount": 200.00, "mcc": "6011"},
    {"id": "t10", "raw_description": "Spotify Subscription", "amount": 9.99, "mcc": "4899"},
    {"id": "t11", "raw_description": "Electricity Bill Payment", "amount": 120.00, "mcc": "4900"},
    {"id": "t12", "raw_description": "Internal Transfer", "amount": 500.00, "mcc": "4829"},
    {"id": "t13", "raw_description": "Bank Fee", "amount": 2.50, "mcc": "6012"},
    {"id": "t14", "raw_description": "Pharmacy POS", "amount": 25.00, "mcc": "5912"},
    {"id": "t15", "raw_description": "Water Bill Payment", "amount": 45.00, "mcc": "4931"},
    {"id": "t16", "raw_description": "NETFLIX Subscription Shopping", "amount": 15.49, "mcc": "5942"},
    {"id": "t17", "raw_description": "UBER TRIP Fast Food", "amount": 18.20, "mcc": "5814"},
    {"id": "t18", "raw_description": "STARBUCKS STORE #123 Fast Food", "amount": 6.75, "mcc": "5814"},
]

def seed():
    session: Session = SessionLocal()

    # Ensure the test user exists
    test_user = session.query(models.UserORM).filter_by(user_id="user_42").first()
    if not test_user:
        test_user = models.UserORM(
            user_id="user_42",
            name="BhanuPrakash",
            email="bhanu@example.com",
            created_at=datetime.fromisoformat("2025-09-01T06:06:07.450004"),
        )
        session.add(test_user)
        session.commit()

    # Seed merchants
    for m in MERCHANTS:
        if not session.query(models.MerchantORM).filter_by(merchant_id=m["merchant_id"]).first():
            merchant = models.MerchantORM(
                merchant_id=m["merchant_id"],
                display_name=m["display_name"],
                aliases=m["aliases"],
                default_category=m["default_category"],
                typical_mccs=m["typical_mccs"],
            )
            session.add(merchant)

    # Add fallback uncategorized merchant
    uncategorized = session.query(models.MerchantORM).filter_by(merchant_id="m_uncategorized").first()
    if not uncategorized:
        uncategorized = models.MerchantORM(
            merchant_id="m_uncategorized",
            display_name="Uncategorized",
            aliases=[],
            default_category="Uncategorized",
            typical_mccs=[],
        )
        session.add(uncategorized)

    session.commit()

    # Seed transactions
    for t in TRANSACTIONS:
        if not session.query(models.TransactionORM).filter_by(id=t["id"]).first():
            merchant = None
            for m in MERCHANTS:
                if any(alias.lower() in t["raw_description"].lower() for alias in m["aliases"]):
                    merchant = session.query(models.MerchantORM).filter_by(merchant_id=m["merchant_id"]).first()
                    break
                if t["mcc"] in m["typical_mccs"]:
                    merchant = session.query(models.MerchantORM).filter_by(merchant_id=m["merchant_id"]).first()
                    break

            txn = models.TransactionORM(
                id=t["id"],
                user_id="user_42",
                merchant_id=merchant.merchant_id if merchant else "m_uncategorized",
                raw_description=t["raw_description"],
                amount=t["amount"],
                currency="INR",
                mcc=t["mcc"],
                posted_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                geo={}
            )
            session.add(txn)

    session.commit()
    session.close()
    print(" Seed completed: user + merchants + transactions")

if __name__ == "__main__":
    seed()