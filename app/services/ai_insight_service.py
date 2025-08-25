import google.generativeai as genai
from typing import Dict, List, Any
import json
from datetime import datetime, timedelta
from fastapi import Depends

from app import settings
from app.db.session import get_db
from sqlalchemy.orm import Session

class AIInsightService:
    """Service for generating AI-powered financial insights."""
    
    def __init__(self, db: Session):
        self.db = db
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive financial insights for a user."""
        # Get financial data (simplified for example)
        financial_data = self._get_user_financial_data(user_id)
        
        # Generate prompt
        prompt = self._create_insight_prompt(financial_data)
        
        try:
            # Get AI response
            response = await self.model.generate_content_async(prompt)
            insights = response.text
            
            # Parse and structure the response
            return self._parse_insights(insights)
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate insights: {str(e)}"
            }
    
    def _get_user_financial_data(self, user_id: str) -> Dict[str, Any]:
        """Get user's financial data from the database."""
        # In a real implementation, this would query the database
        # For now, return a simplified structure
        return {
            "net_worth": {"current": 1000000, "trend": "increasing"},
            "expenses": {"monthly_average": 50000, "categories": {"food": 30, "housing": 40, "transport": 15, "other": 15}},
            "investments": {"total": 700000, "allocation": {"equity": 60, "debt": 30, "others": 10}},
            "liabilities": {"total": 200000, "breakdown": [{"type": "loan", "amount": 200000, "interest_rate": 9.5}]},
            "goals": [{"name": "Retirement", "target": 5000000, "current": 700000, "timeline": 15}]
        }
    
    def _create_insight_prompt(self, financial_data: Dict[str, Any]) -> str:
        """Create a prompt for the AI model."""
        return f"""
        You are a financial advisor analyzing a user's financial situation.
        Provide a comprehensive analysis with the following sections:
        
        1. Net Worth Summary: Current status and trend
        2. Spending Analysis: Key observations about spending patterns
        3. Investment Review: Asset allocation and recommendations
        4. Debt Management: Analysis of current liabilities
        5. Goal Progress: Status of financial goals
        6. Key Recommendations: 3-5 actionable insights
        
        Financial Data:
        {json.dumps(financial_data, indent=2)}
        
        Format the response as a JSON object with these keys:
        - net_worth_summary
        - spending_analysis
        - investment_review
        - debt_analysis
        - goal_progress
        - recommendations (array of strings)
        """
    
    def _parse_insights(self, ai_response: str) -> Dict[str, Any]:
        """Parse the AI response into a structured format."""
        try:
            # Try to parse as JSON
            start = ai_response.find('{')
            end = ai_response.rfind('}') + 1
            json_str = ai_response[start:end]
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If parsing fails, return as raw text
            return {"raw_insights": ai_response}

def get_ai_insight_service(db: Session = Depends(get_db)) -> AIInsightService:
    return AIInsightService(db)
