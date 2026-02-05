#Base provider interface for LLM abstraction

# Used to create abstract base classes
from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum

# Base error for all provider-related problems
class ProviderError(Exception):
    
    pass

# Error when API rate limit is exceeded
class RateLimitError(ProviderError):
    
    pass

# Error when request takes too long
class TimeoutError(ProviderError):
    
    pass

# Error when model is not available
class ModelUnavailableError(ProviderError):
    
    pass

# Standard error categories used across all providers
class ErrorType(Enum):
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    PROVIDER_ERROR = "provider_error"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN = "unknown"

# This is the parent class for all LLM providers (OpenAI, Groq, etc.)
class BaseProvider(ABC):
    
    def __init__(self, provider_name: str):
        # Store provider name (used for tracking & logging)
        self.provider_name = provider_name
    
    @abstractmethod
    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
       # This method sends request to LLM and returns response

        pass
    
    # Convert provider response into a common format
    def normalize_response(self, raw_response: Any, model: str) -> Dict[str, Any]:
        
        raise NotImplementedError
    
    # Convert provider-specific errors into standard error types
    def normalize_error(self, error: Exception) -> tuple[ErrorType, str]:
        
        error_msg = str(error).lower()
        
        # Detect rate limit errors
        if "rate" in error_msg or "429" in error_msg:
            return ErrorType.RATE_LIMIT, str(error)
        # Detect timeout errors
        elif "timeout" in error_msg or "timed out" in error_msg:
            return ErrorType.TIMEOUT, str(error)
        # Detect invalid request errors
        elif "invalid" in error_msg or "400" in error_msg:
            return ErrorType.INVALID_REQUEST, str(error)
        else:
            return ErrorType.UNKNOWN, str(error)




