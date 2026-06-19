from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserFinancialData(BaseModel):
    name: str = Field(..., example="أحمد الخالدي")
    profession: str = Field(..., example="Uber Driver")
    profession_category: str = Field(..., example="gig")
    avg_monthly_income_jod: float = Field(..., gt=0)
    income_stability_score: float = Field(..., ge=0, le=1)
    income_source_count: int = Field(..., ge=1)
    late_bills_count: int = Field(..., ge=0)
    bill_reliability_pct: float = Field(..., ge=0, le=100)
    total_bills_checked: int = Field(..., ge=0)
    current_balance_jod: float = Field(..., ge=0)
    wallet_tx_count: int = Field(..., ge=0)
    wallet_total_volume_jod: float = Field(..., ge=0)
    balance_to_income_ratio: float = Field(..., ge=0)
    existing_loans: int = Field(..., ge=0)
    
    # Loan Context
    requested_amount_jod: Optional[int] = Field(500, example=500)
    loan_duration_months: Optional[int] = Field(12, example=12)
    interest_rate: Optional[float] = Field(0.12, example=0.12)

class ScoreBreakdown(BaseModel):
    income_stability: float
    bill_history: float
    financial_health: float

class ScoringResult(BaseModel):
    ml_score: float
    llm_adjusted_score: float
    final_score: float
    risk_level: str
    decision: str
    approved_amount_jod: int
    score_breakdown: ScoreBreakdown
    key_strengths: List[str]
    key_risks: List[str]
    reason: str
    applicant_name: str
    profession: str
    timestamp: str
    confidence: str

class UserProfile(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime

class ChatRequest(BaseModel):
    user_id: str
    message: str
    role: str = "user"

class ChatResponse(BaseModel):
    response: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ImprovementPlanRequest(BaseModel):
    user_id: str
    email: str
