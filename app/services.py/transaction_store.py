"""
Transaction storage service
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

from app.models.schemas import TransactionConfirmation, DecimalEncoder

logger = logging.getLogger(__name__)

class TransactionStore:
    """Handles persistence of transaction data"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure storage directory and file exist"""
        self.file_path.parent.mkdir(exist_ok=True, parents=True)
        if not self.file_path.exists():
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def load_transactions(self) -> List[Dict[str, Any]]:
        """Load transactions from storage"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading transactions: {e}")
            return []
    
    def save_transaction(self, tx: TransactionConfirmation):
        """Save transaction to storage"""
        try:
            transactions = self.load_transactions()
            transactions.append(tx.to_dict())
            
            with open(self.file_path, 'w') as f:
                json.dump(transactions, f, indent=2, cls=DecimalEncoder)
                
            logger.info(f"Transaction saved: {tx.tx_hash}")
        except Exception as e:
            logger.error(f"Failed to save transaction: {e}")