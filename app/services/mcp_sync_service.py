import uuid
from datetime import datetime
from typing import Dict, List, Any
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.fi_mcp_client import FiMCPClient, get_fi_mcp_client
from app.models.mcp_models import FinancialSnapshot, Asset, Liability, CreditScore, EPFAccount
from app.db.session import get_db

class MCPSyncService:
    """Service for syncing data from Fi's MCP Server."""
    
    def __init__(self, db: Session, mcp_client: FiMCPClient):
        self.db = db
        self.mcp_client = mcp_client
    
    async def sync_user_data(self, user_id: str) -> Dict[str, Any]:
        """Sync all financial data for a user."""
        try:
            # 1. Get financial snapshot
            snapshot = await self.mcp_client.get_financial_snapshot(user_id)
            
            # 2. Save assets
            for asset in snapshot.get('assets', []):
                self._save_asset(user_id, asset)
            
            # 3. Save liabilities
            for liability in snapshot.get('liabilities', []):
                self._save_liability(user_id, liability)
            
            # 4. Save credit score if available
            if 'credit_score' in snapshot:
                self._save_credit_score(user_id, snapshot['credit_score'])
            
            # 5. Save EPF details if available
            if 'epf' in snapshot:
                self._save_epf(user_id, snapshot['epf'])
            
            # 6. Create financial snapshot
            self._create_snapshot(user_id, snapshot)
            
            self.db.commit()
            return {"status": "success", "message": "Data synced successfully"}
            
        except Exception as e:
            self.db.rollback()
            return {"status": "error", "message": str(e)}
    
    def _save_asset(self, user_id: str, asset_data: Dict[str, Any]):
        """Save or update an asset."""
        asset = self.db.query(Asset).filter(Asset.id == asset_data['id']).first()
        if not asset:
            asset = Asset(id=asset_data['id'], user_id=user_id)
            self.db.add(asset)
        
        # Update fields
        for field in ['name', 'type', 'current_value', 'currency']:
            if field in asset_data:
                setattr(asset, field, asset_data[field])
    
    def _save_liability(self, user_id: str, liability_data: Dict[str, Any]):
        """Save or update a liability."""
        liability = self.db.query(Liability).filter(Liability.id == liability_data['id']).first()
        if not liability:
            liability = Liability(id=liability_data['id'], user_id=user_id)
            self.db.add(liability)
        
        # Update fields
        for field in ['name', 'type', 'outstanding_amount', 'currency', 'interest_rate']:
            if field in liability_data:
                setattr(liability, field, liability_data[field])
    
    def _save_credit_score(self, user_id: str, score_data: Dict[str, Any]):
        """Save credit score information."""
        score = CreditScore(
            user_id=user_id,
            score=score_data.get('score'),
            provider=score_data.get('provider', 'unknown'),
            factors=score_data.get('factors')
        )
        self.db.add(score)
    
    def _save_epf(self, user_id: str, epf_data: Dict[str, Any]):
        """Save EPF account details."""
        epf = EPFAccount(
            id=epf_data.get('account_number', str(uuid.uuid4())),
            user_id=user_id,
            current_balance=epf_data.get('current_balance', 0),
            employer_contribution=epf_data.get('employer_contribution'),
            employee_contribution=epf_data.get('employee_contribution'),
            interest_rate=epf_data.get('interest_rate')
        )
        self.db.add(epf)
    
    def _create_snapshot(self, user_id: str, snapshot_data: Dict[str, Any]):
        """Create a financial snapshot."""
        snapshot = FinancialSnapshot(
            user_id=user_id,
            total_assets=snapshot_data.get('total_assets', 0),
            total_liabilities=snapshot_data.get('total_liabilities', 0),
            net_worth=snapshot_data.get('net_worth', 0),
            raw_data=snapshot_data
        )
        self.db.add(snapshot)

def get_mcp_sync_service(
    db: Session = Depends(get_db),
    mcp_client: FiMCPClient = Depends(get_fi_mcp_client)
) -> MCPSyncService:
    return MCPSyncService(db, mcp_client)
