#Configuration management for LLM Orchestrator

import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Main configuration class for the project
class Config:
    
    # API keys for different providers
    # These are read from environment variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Token and request related settings
    # Max tokens before cooldown is applied
    TOKEN_COOLDOWN_THRESHOLD = int(os.getenv("TOKEN_COOLDOWN_THRESHOLD", "5000"))
    COOLDOWN_DURATION_SECONDS = int(os.getenv("COOLDOWN_DURATION_SECONDS", "300"))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # Configuration for each supported model
    MODEL_CONFIG = {
        "gpt-4": {
            "provider": "openai",
            "cost_per_1k": 0.03,
            "speed": "slow",
            "quality": "high",
            "capabilities": ["code", "reasoning", "writing", "complex"]
        },
        "gpt-3.5-turbo": {
            "provider": "openai",
            "cost_per_1k": 0.001,
            "speed": "fast",
            "quality": "medium",
            "capabilities": ["general", "writing", "simple"]
        },
        "claude-sonnet-4": {
            "provider": "anthropic",
            "cost_per_1k": 0.015,
            "speed": "medium",
            "quality": "high",
            "capabilities": ["reasoning", "writing", "analysis"]
        },
        "claude-haiku-4": {
            "provider": "anthropic",
            "cost_per_1k": 0.0008,
            "speed": "very_fast",
            "quality": "medium",
            "capabilities": ["general", "simple", "fast"]
        }
    }
    
    # Intent to Model Mapping
    INTENT_ROUTING = {
        "code_generation": ["gpt-4", "gpt-3.5-turbo"],
        "education": ["gpt-4", "claude-sonnet-4", "gpt-3.5-turbo"],
        "writing": ["claude-sonnet-4", "gpt-4", "gpt-3.5-turbo"],
        "translation": ["gpt-3.5-turbo", "claude-haiku-4"],
        "summarization": ["claude-haiku-4", "gpt-3.5-turbo"],
        "general": ["gpt-3.5-turbo", "claude-haiku-4"]
    }

config = Config()