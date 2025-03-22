"""
Application configuration settings
"""
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
    
    # New settings from your .env file
    MAINNET_CHAIN_ID: str = Field(default="1", env="MAINNET_CHAIN_ID")
    SESSION_ENCRYPTION_KEY: str = Field(default="", env="SESSION_ENCRYPTION_KEY")
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings object
settings = Settings()

# Ensure data directory exists
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)