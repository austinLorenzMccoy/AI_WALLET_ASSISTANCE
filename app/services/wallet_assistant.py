"""
Core wallet assistant service
"""
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from web3 import Web3

from app.core.config import settings
from app.services.ai_parser import AIParser
from app.services.transaction_store import TransactionStore
from app.models.schemas import (
    TransactionIntent, WalletState, WalletCommand, 
    TransactionConfirmation
)

logger = logging.getLogger(__name__)

class AIWalletAssistant:
    """Core wallet assistant that processes commands and manages transactions"""
    
    def __init__(self):
        # Initialize components
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            raise EnvironmentError("GROQ_API_KEY not found in environment variables")
            
        self.parser = AIParser(self.api_key)
        self.store = TransactionStore(settings.TRANSACTIONS_FILE)
        
        # Initialize Web3 with provider from environment
        ethereum_node_url = settings.ETHEREUM_NODE_URL
        if ethereum_node_url:
            self.web3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{ethereum_node_url}"))
        else:
            # Fallback to local provider for testing
            self.web3 = Web3()
            logger.warning("Using default Web3 provider. Set ETHEREUM_NODE_URL for production.")
    
    async def process_command(self, user_input: str, wallet_state: WalletState) -> Dict[str, Any]:
        """Process user command and return appropriate response"""
        try:
            # Parse natural language command
            intent = await self.parser.parse_command(user_input)
            
            # Process based on command type
            if intent.action == WalletCommand.SEND:
                return await self._handle_send(intent, wallet_state)
                
            elif intent.action == WalletCommand.BALANCE:
                return self._handle_balance(wallet_state)
                
            elif intent.action == WalletCommand.HISTORY:
                return self._handle_history(wallet_state)
                
            elif intent.action == WalletCommand.SWAP:
                return await self._handle_swap(intent, wallet_state)
                
            elif intent.action == WalletCommand.HELP:
                return self._handle_help()
                
            else:
                return {
                    "error": f"Unsupported action: {intent.action}",
                    "suggestion": "Try 'send', 'balance', 'history', or 'help'"
                }
                
        except ValueError as e:
            logger.error(f"Command processing error: {e}")
            return {
                "error": str(e),
                "suggestion": "Try formatting like: 'Send 0.1 ETH to 0x...'"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "error": "An unexpected error occurred",
                "suggestion": "Please try again with a simpler command"
            }

    async def _handle_send(self, intent: TransactionIntent, wallet_state: WalletState) -> Dict[str, Any]:
        """Handle send transaction command"""
        # Validate recipient address
        if not intent.recipient or not self.web3.is_address(intent.recipient):
            raise ValueError("Invalid recipient address")
        
        # Validate asset and amount
        if not intent.asset or not intent.amount:
            raise ValueError("Missing asset or amount")
            
        # Check balance
        if wallet_state.balance.get(intent.asset, 0) < intent.amount:
            raise ValueError(f"Insufficient balance: {wallet_state.balance.get(intent.asset, 0)} {intent.asset}")
        
        # Build transaction
        gas_price = self.web3.eth.gas_price
        gas_limit = 21000  # Default gas limit for ETH transfers
        
        tx_data = {
            'from': wallet_state.address,
            'to': intent.recipient,
            'value': self.web3.to_wei(intent.amount, 'ether'),
            'gasPrice': float(gas_price),  # Convert Decimal to float
            'gas': gas_limit
        }
        
        # Calculate gas estimate in ETH
        gas_estimate = float(gas_price * gas_limit) / 1e18  # Convert wei to ETH
        
        # Return payload for MetaMask confirmation
        return {
            "action": "send",
            "details": {
                "from": wallet_state.address,
                "to": intent.recipient,
                "amount": intent.amount,
                "asset": intent.asset,
                "network": intent.network,
                "gasEstimate": gas_estimate
            },
            "metaMaskPayload": tx_data
        }
    
    def _handle_balance(self, wallet_state: WalletState) -> Dict[str, Any]:
        """Handle balance inquiry command"""
        return {
            "action": "balance",
            "balances": wallet_state.balance,
            "totalValueUSD": sum(amount for asset, amount in wallet_state.balance.items()),
            "network": wallet_state.network
        }
    
    def _handle_history(self, wallet_state: WalletState) -> Dict[str, Any]:
        """Handle transaction history command"""
        return {
            "action": "history",
            "transactions": [tx.to_dict() for tx in wallet_state.transaction_history],
            "pending": [tx.to_dict() for tx in wallet_state.pending_transactions]
        }
    
    async def _handle_swap(self, intent: TransactionIntent, wallet_state: WalletState) -> Dict[str, Any]:
        """Handle swap command"""
        # This would integrate with DEX APIs in production
        return {
            "action": "swap",
            "error": "Swap functionality is not implemented yet",
            "suggestion": "Use 'send' for transfers"
        }
    
    def _handle_help(self) -> Dict[str, Any]:
        """Handle help command"""
        return {
            "action": "help",
            "commands": [
                {"name": "send", "format": "Send [amount] [asset] to [address]"},
                {"name": "balance", "format": "Show my balance"},
                {"name": "history", "format": "Show transaction history"},
                {"name": "swap", "format": "Swap [amount] [asset] for [asset]"}
            ]
        }
    
    def save_transaction(self, tx: TransactionConfirmation):
        """Save transaction to storage"""
        self.store.save_transaction(tx)


class WalletSessionManager:
    """Manages active wallet sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, WalletState] = {}
        self.last_activity: Dict[str, datetime] = {}
        self.assistant = AIWalletAssistant()
    
    def create_session(self, address: str, network: str = "mainnet") -> str:
        """Create a new wallet session"""
        session_id = f"session_{address[:10]}_{datetime.now().timestamp()}"
        
        # Mock balance for testing - would be fetched from blockchain in production
        self.active_sessions[session_id] = WalletState(
            address=address,
            balance={"ETH": 5.0, "USDC": 1000.0},
            network=network
        )
        
        self.last_activity[session_id] = datetime.now()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[WalletState]:
        """Get wallet session by ID"""
        session = self.active_sessions.get(session_id)
        if session:
            self.last_activity[session_id] = datetime.now()
        return session
    
    async def handle_user_request(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """Process user request within a session"""
        wallet_state = self.get_session(session_id)
        if not wallet_state:
            raise ValueError("No active wallet session")
        
        # Process command
        return await self.assistant.process_command(user_input, wallet_state)
    
    def cleanup_inactive_sessions(self):
        """Remove inactive sessions"""
        now = datetime.now()
        inactive_sessions = [
            session_id for session_id, last_active in self.last_activity.items()
            if (now - last_active).total_seconds() > settings.INACTIVITY_TIMEOUT
        ]
        
        for session_id in inactive_sessions:
            del self.active_sessions[session_id]
            del self.last_activity[session_id]
            logger.info(f"Cleaned up inactive session: {session_id}")