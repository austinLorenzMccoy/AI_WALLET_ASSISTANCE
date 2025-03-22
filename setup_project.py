#!/usr/bin/env python3
"""
Setup script for AI Wallet Assistant project structure
"""
import os
import shutil
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Create directory structure
directories = [
    'app',
    'app/api',
    'app/core',
    'app/models',
    'app/services',
    'static',
    'wallet_data',
]

# Create directories
for directory in directories:
    os.makedirs(PROJECT_ROOT / directory, exist_ok=True)

# Create __init__.py files
init_files = [
    'app/__init__.py',
    'app/api/__init__.py',
    'app/core/__init__.py',
    'app/models/__init__.py',
    'app/services/__init__.py',
]

for init_file in init_files:
    with open(PROJECT_ROOT / init_file, 'w') as f:
        f.write('"""Package initialization file"""\n')

# Create/move files to the right locations
file_mapping = {
    # API files
    'dependencies.py': 'app/api/dependencies.py',
    'routes.py': 'app/api/routes.py',
    
    # Core files
    'config.py': 'app/core/config.py',
    'security.py': 'app/core/security.py',
    
    # Models
    'schemas.py': 'app/models/schemas.py',
    
    # Services (from paste.txt)
    'wallet_assistant.py': 'app/services/wallet_assistant.py',
    'ai_parser.py': 'app/services/ai_parser.py',
    'transaction_store.py': 'app/services/transaction_store.py',
    
    # Main application file
    'main.py': 'main.py',
}

# Helper function to extract code sections from paste.txt
def extract_sections_from_paste(paste_content):
    """Extract different class files from the paste.txt content"""
    
    # Sections to extract
    sections = {
        'wallet_assistant.py': {
            'start': 'class AIWalletAssistant:',
            'end': 'class WalletSessionManager:',
            'prefix': '"""\nCore wallet assistant service\n"""\nimport logging\nimport os\nfrom datetime import datetime\nfrom typing import Dict, Any, Optional\n\nfrom web3 import Web3\n\nfrom app.core.config import settings\nfrom app.services.ai_parser import AIParser\nfrom app.services.transaction_store import TransactionStore\nfrom app.models.schemas import (\n    TransactionIntent, WalletState, WalletCommand, \n    TransactionConfirmation\n)\n\nlogger = logging.getLogger(__name__)\n\n'
        },
        'wallet_session_manager.py': {
            'start': 'class WalletSessionManager:',
            'end': None,  # End of file
            'prefix': '"""\nWallet session management service\n"""\nimport logging\nfrom datetime import datetime\nfrom typing import Dict, Any, Optional\n\nfrom app.core.config import settings\nfrom app.services.wallet_assistant import AIWalletAssistant\nfrom app.models.schemas import WalletState\n\nlogger = logging.getLogger(__name__)\n\n'
        },
        'ai_parser.py': {
            'content': '"""\nAI parsing service for natural language commands\n"""\nimport logging\nimport asyncio\nfrom typing import Dict, Any\n\nfrom groq import Groq\n\nfrom app.core.config import settings\nfrom app.models.schemas import TransactionIntent\n\nlogger = logging.getLogger(__name__)\n\nclass AIParser:\n    """Handles parsing user input into structured transaction intents"""\n    \n    def __init__(self, api_key: str):\n        self.groq = Groq(api_key=api_key)\n        self.system_prompt = """You are an AI Wallet Assistant. Parse user commands into structured JSON.\n        Respond ONLY in JSON format: {\n            "action": "send|swap|balance|history",\n            "asset": "asset symbol",\n            "amount": number,\n            "recipient": "address",\n            "network": "network"\n        }"""\n        \n    async def parse_command(self, user_input: str) -> TransactionIntent:\n        """Parse natural language input into structured transaction intent"""\n        try:\n            # Request completion from Groq\n            response = await asyncio.to_thread(\n                self.groq.chat.completions.create,\n                messages=[\n                    {"role": "system", "content": self.system_prompt},\n                    {"role": "user", "content": user_input}\n                ],\n                model="Llama3-8b-8192",\n                temperature=0.1,\n                max_tokens=settings.MAX_TOKENS\n            )\n            \n            # Extract JSON from response\n            json_str = response.choices[0].message.content\n            logger.debug(f"Parsed intent: {json_str}")\n            \n            # Parse JSON into TransactionIntent\n            return TransactionIntent.parse_from_json(json_str)\n            \n        except Exception as e:\n            logger.error(f"Command parsing error: {str(e)}")\n            raise ValueError(f"Could not parse command: {str(e)}")'
        },
        'transaction_store.py': {
            'content': '"""\nTransaction storage service\n"""\nimport json\nimport logging\nfrom pathlib import Path\nfrom typing import List, Dict, Any\n\nfrom app.models.schemas import TransactionConfirmation, DecimalEncoder\n\nlogger = logging.getLogger(__name__)\n\nclass TransactionStore:\n    """Handles persistence of transaction data"""\n    \n    def __init__(self, file_path: Path):\n        self.file_path = file_path\n        self._ensure_storage_exists()\n    \n    def _ensure_storage_exists(self):\n        """Ensure storage directory and file exist"""\n        self.file_path.parent.mkdir(exist_ok=True, parents=True)\n        if not self.file_path.exists():\n            with open(self.file_path, \'w\') as f:\n                json.dump([], f)\n    \n    def load_transactions(self) -> List[Dict[str, Any]]:\n        """Load transactions from storage"""\n        try:\n            with open(self.file_path, \'r\') as f:\n                return json.load(f)\n        except (json.JSONDecodeError, FileNotFoundError) as e:\n            logger.error(f"Error loading transactions: {e}")\n            return []\n    \n    def save_transaction(self, tx: TransactionConfirmation):\n        """Save transaction to storage"""\n        try:\n            transactions = self.load_transactions()\n            transactions.append(tx.to_dict())\n            \n            with open(self.file_path, \'w\') as f:\n                json.dump(transactions, f, indent=2, cls=DecimalEncoder)\n                \n            logger.info(f"Transaction saved: {tx.tx_hash}")\n        except Exception as e:\n            logger.error(f"Failed to save transaction: {e}")'
        }
    }
    
    results = {}
    
    # Extract classes with start/end pattern
    for file_name, section_info in sections.items():
        if 'content' in section_info:
            # Direct content
            results[file_name] = section_info['content']
        else:
            # Extract from paste
            start_marker = section_info['start']
            end_marker = section_info['end']
            prefix = section_info.get('prefix', '')
            
            start_idx = paste_content.find(start_marker)
            
            if start_idx == -1:
                print(f"Could not find start marker '{start_marker}' for {file_name}")
                continue
                
            if end_marker:
                end_idx = paste_content.find(end_marker, start_idx)
                if end_idx == -1:
                    content = paste_content[start_idx:]
                else:
                    content = paste_content[start_idx:end_idx]
            else:
                content = paste_content[start_idx:]
                
            results[file_name] = prefix + content
    
    return results

# Get paste.txt content
paste_content = ""
try:
    with open('paste.txt', 'r') as f:
        paste_content = f.read()
except FileNotFoundError:
    print("paste.txt not found, skipping service file extraction")

# Extract service files from paste.txt
if paste_content:
    service_files = extract_sections_from_paste(paste_content)
    for file_name, content in service_files.items():
        # If it's the session manager, put it in wallet_assistant.py
        if file_name == 'wallet_session_manager.py':
            with open('app/services/wallet_assistant.py', 'a') as f:
                f.write('\n\n' + content)
        else:
            target_path = f'app/services/{file_name}'
            with open(target_path, 'w') as f:
                f.write(content)

# Create core files
config_py = """
\"\"\"
Application configuration settings
\"\"\"
from typing import List
from pathlib import Path
import os

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "AI Wallet Assistant"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://localhost:3000"]
    
    # API Keys
    GROQ_API_KEY: str = Field(default="", env="GROQ_API_KEY")
    ETHEREUM_NODE_URL: str = Field(default="", env="ETHEREUM_NODE_URL")
    
    # Session Management
    INACTIVITY_TIMEOUT: int = 300  # 5 minutes
    MAX_TOKENS: int = 1024
    
    # Storage
    DATA_DIR: Path = Path("wallet_data")
    TRANSACTIONS_FILE: Path = DATA_DIR / "transactions.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings object
settings = Settings()

# Ensure data directory exists
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
"""

security_py = """
\"\"\"
Security and validation functions
\"\"\"
import logging
from web3 import Web3
from app.models.schemas import WalletState

logger = logging.getLogger(__name__)

class SecurityValidator:
    @staticmethod
    def validate_eth_address(address: str) -> bool:
        \"\"\"Validate Ethereum address format\"\"\"
        try:
            return Web3.is_address(address)
        except Exception as e:
            logger.error(f"Address validation error: {e}")
            return False

    @staticmethod
    def validate_balance(wallet_state: WalletState, asset: str, amount: float) -> bool:
        \"\"\"Check if wallet has sufficient balance for transaction\"\"\"
        return wallet_state.balance.get(asset, 0) >= amount
"""

schemas_py = """
\"\"\"
Pydantic models for data validation and serialization
\"\"\"
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
        \"\"\"Parse JSON string into TransactionIntent object with error handling\"\"\"
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
        \"\"\"Convert model to dict with datetime handling\"\"\"
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
"""

# Write core files
with open('app/core/config.py', 'w') as f:
    f.write(config_py.strip())

with open('app/core/security.py', 'w') as f:
    f.write(security_py.strip())

with open('app/models/schemas.py', 'w') as f:
    f.write(schemas_py.strip())

# Copy existing files to their proper locations
file_sources = {
    'dependencies.py': 'app/api/dependencies.py',
    'routes.py': 'app/api/routes.py',
    'helpers.py': 'app/services/helpers.py',
    'main.py': 'main.py'
}

for source, dest in file_sources.items():
    try:
        with open(source, 'r') as src_file, open(dest, 'w') as dest_file:
            dest_file.write(src_file.read())
        print(f"Copied {source} to {dest}")
    except FileNotFoundError:
        print(f"Warning: Could not find {source}")

print("Project structure setup complete!")