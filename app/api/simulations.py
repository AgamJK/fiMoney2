from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum
import math

router = APIRouter()

class LoanType(str, Enum):
    HOME = "home_loan"
    PERSONAL = "personal_loan"
    CAR = "car_loan"
    EDUCATION = "education_loan"

class GoalType(str, Enum):
    RETIREMENT = "retirement"
    HOME_DOWNPAYMENT = "home_downpayment"
    EDUCATION = "education"
    VACATION = "vacation"
    EMERGENCY_FUND = "emergency_fund"
    OTHER = "other"

class LoanSimulationRequest(BaseModel):
    loan_type: LoanType
    amount: float = Field(..., gt=0, description="Loan amount in INR")
    interest_rate: float = Field(..., gt=0, le=30, description="Annual interest rate (e.g., 8.5 for 8.5%)")
    tenure_years: int = Field(..., gt=0, le=30, description="Loan tenure in years")
    current_income: float = Field(..., gt=0, description="Monthly income in INR")
    existing_emis: float = Field(0.0, description="Existing monthly EMIs in INR")
    age: Optional[int] = Field(None, ge=18, le=70, description="Borrower's age")
    property_value: Optional[float] = Field(None, gt=0, description="For home loans, the property value in INR")
    
    @validator('amount')
    def validate_loan_amount(cls, v, values, **kwargs):
        if 'property_value' in values and values.get('property_value'):
            # For home loans, typically max 80% of property value
            if v > values['property_value'] * 0.8:
                raise ValueError("Loan amount cannot exceed 80% of property value")
        return v

class LoanSimulationResponse(BaseModel):
    emi: float
    total_interest: float
    total_payment: float
    emi_to_income_ratio: float
    dti_ratio: float
    emi_breakdown: List[Dict[str, Any]]
    is_affordable: bool
    max_affordable_loan: Optional[float] = None
    suggested_tenure: Optional[int] = None
    
class GoalSimulationRequest(BaseModel):
    goal_type: GoalType
    target_amount: float = Field(..., gt=0, description="Target amount in INR")
    target_date: date = Field(..., description="Target date for the goal")
    current_savings: float = Field(0.0, description="Current savings towards this goal in INR")
    monthly_investment: float = Field(0.0, description="Planned monthly investment in INR")
    expected_return_rate: float = Field(7.0, gt=0, le=20, description="Expected annual return rate (e.g., 12 for 12%)")
    inflation_rate: float = Field(6.0, ge=0, le=15, description="Expected inflation rate")
    
class GoalSimulationResponse(BaseModel):
    months_required: int
    monthly_investment_needed: float
    future_value: float
    inflation_adjusted_amount: float
    is_achievable: bool
    shortfall: Optional[float] = None
    projection: List[Dict[str, Any]]

@router.post("/loan-affordability", response_model=LoanSimulationResponse)
async def simulate_loan_affordability(
    request: LoanSimulationRequest,
    # token: str = Depends(oauth2_scheme)  # Uncomment when auth is implemented
):
    """
    Simulate loan affordability based on user's financial situation
    """
    try:
        # Convert annual rate to monthly and percentage to decimal
        monthly_rate = (request.interest_rate / 100) / 12
        total_emi_months = request.tenure_years * 12
        
        # Calculate EMI using standard formula
        emi = (request.amount * monthly_rate * pow(1 + monthly_rate, total_emi_months)) / \
              (pow(1 + monthly_rate, total_emi_months) - 1)
        
        total_payment = emi * total_emi_months
        total_interest = total_payment - request.amount
        
        # Calculate financial ratios
        emi_to_income_ratio = (emi / request.current_income) * 100
        dti_ratio = ((emi + request.existing_emis) / request.current_income) * 100
        
        # Generate EMI breakdown (first and last 3 EMIs)
        emi_breakdown = []
        remaining_principal = request.amount
        
        for month in range(1, total_emi_months + 1):
            interest_component = remaining_principal * monthly_rate
            principal_component = emi - interest_component
            remaining_principal -= principal_component
            
            # Only include first 3 and last 3 EMIs in breakdown
            if month <= 3 or month > total_emi_months - 3:
                emi_breakdown.append({
                    "month": month,
                    "emi": round(emi, 2),
                    "principal": round(principal_component, 2),
                    "interest": round(interest_component, 2),
                    "remaining_principal": max(0, round(remaining_principal, 2))
                })
            
            # Add ellipsis after first 3 EMIs
            if month == 3 and total_emi_months > 6:
                emi_breakdown.append({"month": "...", "note": f"{total_emi_months - 6} EMIs not shown"})
        
        # Determine affordability (general guideline: EMI <= 40% of income)
        is_affordable = (emi + request.existing_emis) <= (request.current_income * 0.4)
        
        # If not affordable, suggest max loan amount or longer tenure
        max_affordable_loan = None
        suggested_tenure = None
        
        if not is_affordable:
            # Calculate max EMI based on 40% of income
            max_emi = request.current_income * 0.4 - request.existing_emis
            if max_emi > 0:
                # Calculate max loan amount for same tenure
                max_affordable_loan = (max_emi * (pow(1 + monthly_rate, total_emi_months) - 1)) / \
                                    (monthly_rate * pow(1 + monthly_rate, total_emi_months))
                
                # If max_affordable_loan is too low, suggest longer tenure
                if max_affordable_loan < request.amount * 0.7:  # If less than 70% of requested
                    # Find minimum tenure where EMI is affordable
                    for years in range(request.tenure_years + 1, 31):
                        months = years * 12
                        emi_new = (request.amount * monthly_rate * pow(1 + monthly_rate, months)) / \
                                 (pow(1 + monthly_rate, months) - 1)
                        if emi_new <= max_emi:
                            suggested_tenure = years
                            break
        
        return {
            "emi": round(emi, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2),
            "emi_to_income_ratio": round(emi_to_income_ratio, 2),
            "dti_ratio": round(dti_ratio, 2),
            "emi_breakdown": emi_breakdown,
            "is_affordable": is_affordable,
            "max_affordable_loan": round(max_affordable_loan, 2) if max_affordable_loan else None,
            "suggested_tenure": suggested_tenure
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/goal-planning", response_model=GoalSimulationResponse)
async def simulate_goal_planning(
    request: GoalSimulationRequest,
    # token: str = Depends(oauth2_scheme)  # Uncomment when auth is implemented
):
    """
    Simulate goal planning and investment requirements
    """
    try:
        # Calculate time to goal in months
        today = date.today()
        months_to_goal = (request.target_date.year - today.year) * 12 + (request.target_date.month - today.month)
        
        if months_to_goal <= 0:
            raise ValueError("Target date must be in the future")
        
        # Convert annual rates to monthly
        monthly_return_rate = (request.expected_return_rate / 100) / 12
        monthly_inflation_rate = (request.inflation_rate / 100) / 12
        
        # Calculate inflation-adjusted target amount
        inflation_factor = pow(1 + monthly_inflation_rate, months_to_goal)
        inflation_adjusted_amount = request.target_amount * inflation_factor
        
        # Calculate future value of current savings
        if request.current_savings > 0:
            fv_current = request.current_savings * pow(1 + monthly_return_rate, months_to_goal)
        else:
            fv_current = 0
        
        # Calculate required monthly investment to reach goal
        if request.monthly_investment > 0:
            # Calculate FV of planned monthly investments
            fv_planned = request.monthly_investment * \
                        ((pow(1 + monthly_return_rate, months_to_goal) - 1) / monthly_return_rate) * \
                        (1 + monthly_return_rate)
            
            total_fv = fv_current + fv_planned
            is_achievable = total_fv >= inflation_adjusted_amount
            shortfall = max(0, inflation_adjusted_amount - total_fv) if not is_achievable else None
            
            # If there's a shortfall, calculate required monthly investment
            if shortfall:
                required_fv = inflation_adjusted_amount - fv_current
                if required_fv > 0:
                    monthly_investment_needed = (required_fv * monthly_return_rate) / \
                                              ((pow(1 + monthly_return_rate, months_to_goal) - 1) * \
                                               (1 + monthly_return_rate))
                else:
                    monthly_investment_needed = 0
            else:
                monthly_investment_needed = request.monthly_investment
        else:
            # Calculate required monthly investment from scratch
            required_fv = inflation_adjusted_amount - fv_current
            if required_fv > 0:
                monthly_investment_needed = (required_fv * monthly_return_rate) / \
                                          ((pow(1 + monthly_return_rate, months_to_goal) - 1) * \
                                           (1 + monthly_return_rate))
            else:
                monthly_investment_needed = 0
            
            is_achievable = monthly_investment_needed >= 0
            shortfall = None if is_achievable else abs(required_fv)
        
        # Generate projection (annual points for long-term goals, quarterly for short-term)
        projection_interval = 3 if months_to_goal <= 24 else 12
        projection = []
        
        for month in range(0, months_to_goal + 1, projection_interval):
            if month == 0:
                # Current month
                fv_savings = request.current_savings
                fv_investments = 0
                total = fv_savings
            else:
                # Future months
                fv_savings = request.current_savings * pow(1 + monthly_return_rate, month)
                if monthly_investment_needed > 0:
                    fv_investments = monthly_investment_needed * \
                                   ((pow(1 + monthly_return_rate, month) - 1) / monthly_return_rate) * \
                                   (1 + monthly_return_rate)
                else:
                    fv_investments = 0
                total = fv_savings + fv_investments
            
            projection.append({
                "month": month,
                "year": (today.year + (today.month - 1 + month) // 12),
                "month_name": (today.month + month - 1) % 12 + 1,
                "current_savings_fv": round(fv_savings, 2),
                "investments_fv": round(fv_investments, 2),
                "total": round(total, 2),
                "target": round(inflation_adjusted_amount, 2) if month == months_to_goal else None
            })
        
        return {
            "months_required": months_to_goal,
            "monthly_investment_needed": round(monthly_investment_needed, 2),
            "future_value": round(fv_current + (monthly_investment_needed * 
                              ((pow(1 + monthly_return_rate, months_to_goal) - 1) / monthly_return_rate) * 
                              (1 + monthly_return_rate)), 2),
            "inflation_adjusted_amount": round(inflation_adjusted_amount, 2),
            "is_achievable": is_achievable,
            "shortfall": round(shortfall, 2) if shortfall is not None else None,
            "projection": projection
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
