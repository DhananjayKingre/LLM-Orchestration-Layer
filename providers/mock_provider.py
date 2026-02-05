#Mock providers for testing without API costs

import random
import asyncio
from typing import Dict, Any

from .base import BaseProvider, RateLimitError, TimeoutError, ProviderError

# Mock provider that always returns a successful response
class MockSuccessProvider(BaseProvider):
    
    def __init__(self):
        # Set provider name as mock_success
        super().__init__("mock_success")
    
    # Simulate a successful model response
    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
    
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        tokens = random.randint(80, 150)
        
        return {
            "text": f"[MOCK SUCCESS] Response to: {prompt[:50]}...",
            "tokens": tokens,
            "prompt_tokens": len(prompt.split()) * 2,
            "completion_tokens": tokens - (len(prompt.split()) * 2),
            "model": model,
            "provider": self.provider_name,
            "metadata": {
                "latency_seconds": 0.1,
                "finish_reason": "stop"
            }
        }

# Mock provider that always throws an error
class MockFailureProvider(BaseProvider):
   
    def __init__(self):
        super().__init__("mock_failure")
    
    # Simulate a failed model call
    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
       
        await asyncio.sleep(0.05)
        raise ProviderError("Simulated provider failure")

# Mock provider that simulates rate limit after few calls
class MockRateLimitProvider(BaseProvider):
    
    def __init__(self):
        super().__init__("mock_ratelimit")
        self.call_count = 0
    
    # Simulate rate limiting after 3 calls
    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:

        self.call_count += 1
        
        if self.call_count > 3:
            raise RateLimitError("Simulated rate limit exceeded")
        
        await asyncio.sleep(0.1)
        # Return fake response before rate limit hits
        return {
            "text": f"[MOCK RATELIMIT] Call {self.call_count}: {prompt[:30]}...",
            "tokens": 100,
            "prompt_tokens": 50,
            "completion_tokens": 50,
            "model": model,
            "provider": self.provider_name,
            "metadata": {"latency_seconds": 0.1}
        }