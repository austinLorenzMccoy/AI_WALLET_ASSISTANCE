"""
API dependencies for FastAPI
"""
from app.services.wallet_assistant import WalletSessionManager

# Singleton instance of session manager
_session_manager = None

def get_session_manager() -> WalletSessionManager:
    """
    Dependency that provides the session manager
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = WalletSessionManager()
    return _session_manager