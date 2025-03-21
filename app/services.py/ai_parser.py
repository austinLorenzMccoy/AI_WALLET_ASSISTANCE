"""
AI parsing service for natural language commands
"""
import logging
import asyncio
from typing import Dict, Any

from groq import Groq

from app.core.config import settings
from app.models.schemas import TransactionIntent

logger = logging.getLogger(__name__)

class AIParser:
    """Handles parsing user input into structured transaction intents"""
    
    def __init__(self, api_key: str):
        self.groq = Groq(api_key=api_key)
        self.system_prompt = """You are an AI Wallet Assistant. Parse user commands into structured JSON.
        Respond ONLY in JSON format: {
            "action": "send|swap|balance|history",
            "asset": "asset symbol",
            "amount": number,
            "recipient": "address",
            "network": "network"
        }"""
        
    async def parse_command(self, user_input: str) -> TransactionIntent:
        """Parse natural language input into structured transaction intent"""
        try:
            # Request completion from Groq
            response = await asyncio.to_thread(
                self.groq.chat.completions.create,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                model="Llama3-8b-8192",
                temperature=0.1,
                max_tokens=settings.MAX_TOKENS
            )
            
            # Extract JSON from response
            json_str = response.choices[0].message.content
            logger.debug(f"Parsed intent: {json_str}")
            
            # Parse JSON into TransactionIntent
            return TransactionIntent.parse_from_json(json_str)
            
        except Exception as e:
            logger.error(f"Command parsing error: {str(e)}")
            raise ValueError(f"Could not parse command: {str(e)}")