import logging
import os
import httpx
from datetime import datetime, date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.exceptions.HighRiskError import HighRiskError
from app.schemas.customer import CustomerCreate
from app.crud import blacklist as crud

logger = logging.getLogger(__name__)

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
    logger.info(f"Calling external fraud detection API at {external_url} for customer {customer_data.email}")
    
    fraud_payload = {
        "name": customer_data.name,
        "address": f"{customer_data.addresses[0].street}, {customer_data.addresses[0].city}, {customer_data.addresses[0].state}, {customer_data.addresses[0].zip_code}, {customer_data.addresses[0].country}" if customer_data.addresses else "Unknown Address",
        "date_of_birth": customer_data.date_of_birth,
        "email": customer_data.email
    }
    
    logger.debug(f"Making async POST request to {external_url} with data: {fraud_payload}")
    
    timeout = httpx.Timeout(30.0)
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                external_url, # type: ignore
                json=fraud_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Fraud API response: {result}")
            
            return {
                "score": result.get("score", 0),
                "category": result.get("category", "LOW")
            }
                
    except httpx.ConnectError as e:
        logger.error(f"Connection error when calling fraud API: {e}")
        raise HTTPException(status_code=503, detail="Cannot connect to fraud detection service") from e
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error when calling fraud API: {e}")
        raise HTTPException(status_code=503, detail="Fraud detection service timeout") from e
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error when calling fraud API: {e} - Status: {e.response.status_code}")
        raise HTTPException(status_code=503, detail="Fraud detection service returned an error") from e
    except httpx.RequestError as e:
        logger.error(f"General request error when calling fraud API: {e}")
        raise HTTPException(status_code=503, detail="Fraud detection service is unavailable") from e
    except Exception as e:
        logger.error(f"Unexpected error when calling fraud API: {e}")
        raise HTTPException(status_code=503, detail="Fraud detection service is unavailable") from e