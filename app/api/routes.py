"""
API routes for the AI Wallet Assistant
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.services.wallet_assistant import WalletSessionManager
from app.models.schemas import (
    ConnectWalletRequest, CommandRequest, 
    SessionResponse, ErrorResponse
)
from app.api.dependencies import get_session_manager

# Set up router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/connect", response_model=SessionResponse)
async def connect_wallet(
    request: ConnectWalletRequest,
    session_manager: WalletSessionManager = Depends(get_session_manager)
):
    """
    Connect a wallet and create a new session
    """
    try:
        session_id = session_manager.create_session(
            address=request.address,
            network=request.network
        )
        
        return SessionResponse(
            session_id=session_id,
            address=request.address,
            network=request.network
        )
    except Exception as e:
        logger.error(f"Failed to connect wallet: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/command")
async def process_command(
    request: CommandRequest,
    background_tasks: BackgroundTasks,
    session_manager: WalletSessionManager = Depends(get_session_manager)
):
    """
    Process a wallet command
    """
    try:
        # Schedule session cleanup in background
        background_tasks.add_task(session_manager.cleanup_inactive_sessions)
        
        # Process the command
        result = await session_manager.handle_user_request(
            user_input=request.command,
            session_id=request.session_id
        )
        
        return result
    except ValueError as e:
        return ErrorResponse(
            error=str(e),
            suggestion="Make sure your session is active and your command is valid"
        )
    except Exception as e:
        logger.error(f"Command processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session/{session_id}")
async def get_session_info(
    session_id: str,
    session_manager: WalletSessionManager = Depends(get_session_manager)
):
    """
    Get information about an active session
    """
    wallet_state = session_manager.get_session(session_id)
    
    if not wallet_state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "address": wallet_state.address,
        "network": wallet_state.network,
        "balances": wallet_state.balance,
        "pending_transactions": len(wallet_state.pending_transactions)
    }