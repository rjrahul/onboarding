import sys
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.exceptions.HighRiskError import HighRiskError
from app.schemas.customer import CustomerCreate
from app.services import risk_assessment

@pytest.mark.asyncio
class TestRiskAssessmentFailures:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def valid_customer(self):
        return CustomerCreate(
            name="Test User",
            email="user@example.com",
            phone="07123456789",
            date_of_birth="2000-05-30",
            addresses=[]
        )

    async def test_fail_on_customer_data_risk(self, mock_db, valid_customer):
        # Force compute_risk_score_based_on_customer_data to return > 30
        with patch.object(
            risk_assessment, "compute_risk_score_based_on_customer_data", return_value=35
        ), patch.object(
            risk_assessment, "compute_risk_score_based_on_blacklist", return_value=False
        ), patch.object(
            risk_assessment, "compute_risk_score_based_on_fraud_api", return_value={"category":"LOW","score":0}
        ):
            with pytest.raises(HighRiskError) as err:
                await risk_assessment.assess_customer_risk(mock_db, valid_customer)
            assert "risk score is very high" in str(err.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("fraud_result", [
        {"category":"HIGH","score":90},
        {"category":"MEDIUM","score":60},
    ])
    async def test_fail_on_fraud_api_high_and_medium(self, mock_db, valid_customer, fraud_result):
        # Patch blacklist to False, customer_data to low risk, fraud_api to high/medium
        with patch.object(
            risk_assessment, "compute_risk_score_based_on_customer_data", return_value=10
        ), patch.object(
            risk_assessment, "compute_risk_score_based_on_blacklist", return_value=False
        ), patch.object(
            risk_assessment, "compute_risk_score_based_on_fraud_api", new=AsyncMock(return_value=fraud_result)
        ):
            with pytest.raises(HighRiskError) as err:
                await risk_assessment.assess_customer_risk(mock_db, valid_customer)
            assert (
                "flagged as high risk by fraud detection service" in str(err.value)
            )

    async def test_fail_on_blacklist(self, mock_db, valid_customer):
        # Patch compute_risk_score_based_on_blacklist to return True
        with patch.object(
            risk_assessment, "compute_risk_score_based_on_blacklist", return_value=True
        ), patch.object(
            risk_assessment, "compute_risk_score_based_on_customer_data", return_value=0
        ), patch.object(
            risk_assessment, "compute_risk_score_based_on_fraud_api", new=AsyncMock(return_value={"category":"LOW","score":0})
        ):
            with pytest.raises(HighRiskError) as err:
                await risk_assessment.assess_customer_risk(mock_db, valid_customer)
            assert "Customer is on the blacklist" in str(err.value)
