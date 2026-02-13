"""
Fraud Detection API: Mock implementation

Provides a POST endpoint to assess customer fraud risk based on name, address, DOB, and email.
- Returns a numeric risk score and a category (LOW, MEDIUM, HIGH)
- Entirely self-contained in this file (no outside dependencies except FastAPI/Pydantic)
- Designed for NFRs: Input validation, error handling, security best practices, readable and extensible
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Dict, Any
import re

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])

class FraudRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    address: str = Field(..., min_length=8, max_length=200)
    date_of_birth: date = Field(..., description="Customer's date of birth (YYYY-MM-DD)")
    email: EmailStr

class FraudResult(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Fraud risk score (0-100, higher = more risky)")
    category: str = Field(..., description="Risk level category")
    reason: Dict[str, Any] = Field(..., description="Breakdown of rationale for the score")

# -- Mock risk factors --
HIGH_RISK_NAMES = {"test", "fraud", "admin", "scam"}
SUSPICIOUS_EMAIL_DOMAINS = {"tempmail.com", "mailinator.com", "demo.com", "fraud.com"}
HIGH_RISK_COUNTRIES = {"Narnia", "Fraudland", "Scamistan"}
MIN_AGE = 18
MAX_AGE = 99

def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def mock_score(request: FraudRequest) -> FraudResult:
    reasons = {}
    score = 0
    # Name check
    lowered = request.name.lower()
    if any(bad in lowered for bad in HIGH_RISK_NAMES):
        score += 40
        reasons['name'] = 'suspicious pattern or word in name'
    # Address country heuristic (very basic for mock)
    country_match = re.search(r'(\b[A-Z][a-zA-Z]+)$', request.address)
    country = country_match.group(1) if country_match else ""
    if country in HIGH_RISK_COUNTRIES:
        score += 30
        reasons['address'] = f'high-risk country detected: {country}'
    # Age check
    age = calculate_age(request.date_of_birth)
    if age < MIN_AGE or age > MAX_AGE:
        score += 15
        reasons['age'] = f'age={age} is outside typical range ({MIN_AGE}-{MAX_AGE})'
    # Email domain heuristic
    domain = request.email.split('@')[-1].lower()
    if domain in SUSPICIOUS_EMAIL_DOMAINS:
        score += 30
        reasons['email'] = f'suspicious email domain: {domain}'
    # Compose result
    capped_score = min(100, score)
    if capped_score >= 71:
        category = "HIGH"
    elif capped_score >= 31:
        category = "MEDIUM"
    else:
        category = "LOW"
    return FraudResult(score=capped_score, category=category, reason=reasons)

@router.post("/fraud-detection", response_model=FraudResult, status_code=status.HTTP_200_OK, tags=["Fraud Detection"], summary="Detect customer fraud risk", responses={400: {"description": "Invalid input"}})
def detect_customer_fraud(request: FraudRequest):
    """
    Predicts the risk of fraud based on customer details.
    - **name**: Customer full name
    - **address**: Customer full address
    - **date_of_birth**: Date of birth (YYYY-MM-DD)
    - **email**: Validated email address
    """
    try:
        result = mock_score(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fraud assessment failed: {str(e)}")
