import os
from unittest import result
from unittest import result
import requests
from datetime import datetime, date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.exceptions.HighRiskError import HighRiskError
from app.schemas.customer import CustomerCreate
from app.crud import blacklist as crud

async def assess_customer_risk(db: Session, customer_data: CustomerCreate):

    if compute_risk_score_based_on_blacklist(db, customer_data):
        raise HighRiskError("Customer is on the blacklist")

    result = await compute_risk_score_based_on_fraud_api(customer_data)
    if result.get("category") == "HIGH":
        raise HighRiskError("Customer is flagged as high risk by fraud detection service")
    elif result.get("category", "LOW") == "MEDIUM" and result.get("score", 0) > 55:
        raise HighRiskError("Customer is flagged as high risk by fraud detection service")

    score = compute_risk_score_based_on_customer_data(customer_data)
    if score > 30:
        raise HighRiskError("Customer risk score is very high")    

    return score

def compute_risk_score_based_on_customer_data(customer_data: CustomerCreate):
    score = 0

    if customer_data.date_of_birth:
        age = (date.today() - datetime.strptime(customer_data.date_of_birth, "%Y-%m-%d").date()).days // 365
        if age < 25:
            score += 20
        elif age < 40:
            score += 10
        else:
            score += 5

    if customer_data.phone and not customer_data.phone.startswith("07"):
        score += 15

    if customer_data.email and customer_data.email.endswith("@example.com"):
        score += 25

    return score


def compute_risk_score_based_on_blacklist(db: Session, customer_data: CustomerCreate):
    blacklist_entry = crud.search_blacklist_by_customer_data(db, customer_data)
    if blacklist_entry:
        return True

    return False

async def compute_risk_score_based_on_fraud_api(customer_data: CustomerCreate):
    external_url = os.getenv("FRAUD_API_URL")
    try:
        response = requests.post(external_url, json=customer_data.model_dump()) # type: ignore
        response.raise_for_status()
        result = response.json()
        
        return {
            "score": result.get("score", 0),
            "category": result.get("category", "LOW")
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail="Fraud detection service is unavailable") from e