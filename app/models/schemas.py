"""
Pydantic models for data validation and serialization
"""
import json
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


# Custom JSON encoder for Decimal values
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class WalletCommand(str, Enum):
    SEND = "send"
    SWAP = "swap"
    BALANCE = "balance"
    HISTORY = "history"
    HELP = "help"


class TransactionIntent(BaseModel):
    action: WalletCommand
    asset: Optional[str] = None
    amount: Optional[float] = None
    recipient: Optional[str] = None
    network: str = "mainnet"
    
    @classmethod
    def parse_from_json(cls, json_str: str) -> "TransactionIntent":
        """Parse JSON string into TransactionIntent object with error handling"""
        try:
            data = json.loads(json_str)
            return cls(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except ValidationError as e:
            raise ValueError(f"Invalid transaction data: {e}")


class TransactionConfirmation(BaseModel):
    tx_hash: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    gas_used: float
    gas_price: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dict with datetime handling"""
        result = self.model_dump()
        # Convert datetime to string for JSON serialization
        result["timestamp"] = self.timestamp.isoformat()
        return result


class WalletMessage(BaseModel):
    role: str  # user|system|assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict] = None


class WalletState(BaseModel):
    address: str
    balance: Dict[str, float]  # {asset: balance}
    pending_transactions: List[TransactionConfirmation] = []
    transaction_history: List[TransactionConfirmation] = []
    network: str = "mainnet"


# API Request/Response Models
class ConnectWalletRequest(BaseModel):
    address: str
    network: str = "mainnet"


class CommandRequest(BaseModel):
    session_id: str
    command: str


class SessionResponse(BaseModel):
    session_id: str
    address: str
    network: str
    created_at: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    error: str
    suggestion: Optional[str] = None