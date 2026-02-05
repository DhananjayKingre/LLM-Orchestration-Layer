#Provider initialization and registry

from .base import BaseProvider, ProviderError, RateLimitError, TimeoutError, ErrorType
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .mock_provider import MockSuccessProvider, MockFailureProvider, MockRateLimitProvider

# Provider registry
PROVIDERS = {}

# Initialize and register all available providers
def initialize_providers():
   
    global PROVIDERS
    
    # Always register mock providers (used for testing)
    PROVIDERS["mock_success"] = MockSuccessProvider()
    PROVIDERS["mock_failure"] = MockFailureProvider()
    PROVIDERS["mock_ratelimit"] = MockRateLimitProvider()
    
    # Try to initialize OpenAI provider
    try:
        PROVIDERS["openai"] = OpenAIProvider()
        print("✓ OpenAI provider initialized")
    except Exception as e:
        print(f"⚠ OpenAI provider not available: {e}")
    
    # Try to initialize Anthropic provider
    try:
        anthropic = AnthropicProvider()
        # Only add if client is properly created
        if anthropic.client:
            PROVIDERS["anthropic"] = anthropic
            print("✓ Anthropic provider initialized")
    except Exception as e:
        print(f"⚠ Anthropic provider not available: {e}")
    
    return PROVIDERS

# Get provider instance by name
def get_provider(provider_name: str) -> BaseProvider:
    
    if not PROVIDERS:
        initialize_providers()
    
    # Check if provider exists
    if provider_name not in PROVIDERS:
        raise ValueError(f"Provider '{provider_name}' not found")
    
    return PROVIDERS[provider_name]

# Exported symbols for this module
__all__ = [
    "BaseProvider",
    "ProviderError",
    "RateLimitError",
    "TimeoutError",
    "ErrorType",
    "initialize_providers",
    "get_provider",
    "PROVIDERS"
]