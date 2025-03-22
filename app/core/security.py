"""
Security and validation functions
"""
import logging
from web3 import Web3
from app.models.schemas import WalletState

logger = logging.getLogger(__name__)

class SecurityValidator:
    @staticmethod
    def validate_eth_address(address: str) -> bool:
        """Validate Ethereum address format"""
        try:
            return Web3.is_address(address)
        except Exception as e:
            logger.error(f"Address validation error: {e}")
            return False

    @staticmethod
    def validate_balance(wallet_state: WalletState, asset: str, amount: float) -> bool:
        """Check if wallet has sufficient balance for transaction"""
        return wallet_state.balance.get(asset, 0) >= amount