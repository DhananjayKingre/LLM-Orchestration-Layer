#Anthropic Provider Implementation

import time
from typing import Dict, Any
from anthropic import AsyncAnthropic
from anthropic import RateLimitError as AnthropicRateLimitError

from .base import BaseProvider, RateLimitError, TimeoutError, ProviderError
from config import config

# Anthropic provider class (Claude models)
class AnthropicProvider(BaseProvider):
   
    
    # Map simplified names to full model names
    MODEL_MAPPING = {
        "claude-sonnet-4": "claude-sonnet-4-20250514",
        "claude-haiku-4": "claude-haiku-4-20250611"
    }
    
    def __init__(self):
        super().__init__("anthropic")
        
        if not config.ANTHROPIC_API_KEY:
            # Don't fail if Anthropic key is missing (optional provider)
            self.client = None
        else:
            self.client = AsyncAnthropic(
                api_key=config.ANTHROPIC_API_KEY,
                timeout=config.REQUEST_TIMEOUT_SECONDS
            )
    
    # Generate response from Anthropic model
    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        
        if not self.client:
            raise ProviderError("Anthropic API key not configured")
        
        # Record start time to calculate latency
        start_time = time.time()
        
        # Convert short model name to full model name
        full_model_name = self.MODEL_MAPPING.get(model, model)
        
        try:
            # Send prompt to Anthropic Messages API
            response = await self.client.messages.create(
                model=full_model_name,
                max_tokens=kwargs.get("max_tokens", 1000),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            latency = time.time() - start_time
            
            return self.normalize_response(response, model, latency)
            
        except AnthropicRateLimitError as e:
            raise RateLimitError(f"Anthropic rate limit exceeded: {e}")
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg:
                raise TimeoutError(f"Anthropic request timed out: {e}")
            raise ProviderError(f"Anthropic error: {e}")
    
    # Convert Anthropic response into common response format
    def normalize_response(self, response: Any, model: str, latency: float) -> Dict[str, Any]:
        
        # Anthropic returns content as a list
        text_content = ""
        for block in response.content:
            if block.type == "text":
                text_content = block.text
                break
        
        # Return standardized response
        return {
            "text": text_content,
            "tokens": response.usage.input_tokens + response.usage.output_tokens,
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "model": model,
            "provider": self.provider_name,
            "metadata": {
                "latency_seconds": round(latency, 2),
                "stop_reason": response.stop_reason
            }
        }