from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class UserFinancialData(BaseModel):
    name: str = Field(..., example="أحمد الخالدي")
    profession: str = Field(..., example="Uber Driver")
    profession_category: str = Field(..., example="gig")
    avg_monthly_income_jod: Decimal = Field(..., gt=0)
    income_stability_score: float = Field(..., ge=0, le=1)
    income_source_count: int = Field(..., ge=1)
    late_bills_count: int = Field(..., ge=0)
    bill_reliability_pct: float = Field(..., ge=0, le=100)
    total_bills_checked: int = Field(..., ge=0)
    current_balance_jod: Decimal = Field(..., ge=0)
    wallet_tx_count: int = Field(..., ge=0)
    wallet_total_volume_jod: Decimal = Field(..., ge=0)
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
    history: list = []

class RetrievalStats(BaseModel):
    generation_time_ms: int = 0
    chunks_retrieved: int = 0
    chunks_used: int = 0

class SourceCitation(BaseModel):
    id: str
    document_name: str
    page: Optional[int] = None
    similarity: float

class ChatResponse(BaseModel):
    response: str
    answer: str
    confidence: Optional[str] = "unknown"
    confidence_score: Optional[float] = 0.0
    support_score: Optional[int] = None
    support_summary: Optional[str] = None
    missing_information: Optional[str] = None
    sources: Optional[List[SourceCitation]] = []
    retrieval_stats: Optional[RetrievalStats] = None
    suggested_followups: Optional[List[str]] = []
    rewritten_info: Optional[dict] = None
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

class TransactionCreate(BaseModel):
    user_email: str
    amount: Decimal
    category: str
    type: str = "expense"
    description: Optional[str] = None
