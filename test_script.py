"""
Test script to validate the AI Wallet Assistant functionality
"""
import asyncio
import json
import logging

from app.services.wallet_assistant import AIWalletAssistant
from app.models.schemas import WalletState, DecimalEncoder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_send_command():
    """Test function to simulate a send command"""
    try:
        # Initialize assistant
        assistant = AIWalletAssistant()
        
        # Create test wallet state
        wallet_state = WalletState(
            address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            balance={"ETH": 5.0, "USDC": 1000.0},
            pending_transactions=[],
            transaction_history=[]
        )
        
        # Process test command
        response = await assistant.process_command(
            "Send 0.1 ETH to 0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            wallet_state
        )
        
        # Use the custom encoder for JSON serialization
        print("Transaction Payload:", json.dumps(response, indent=2, cls=DecimalEncoder))
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        print(f"Test failed: {e}")


if __name__ == '__main__':
    asyncio.run(test_send_command())