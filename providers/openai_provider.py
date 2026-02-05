#OpenAI Provider Implementation

import time
from typing import Dict, Any
from openai import AsyncOpenAI
from openai import RateLimitError as OpenAIRateLimitError
from openai import APITimeoutError as OpenAITimeoutError

from .base import BaseProvider, RateLimitError, TimeoutError, ProviderError
from config import config

# OpenAI provider class (extends BaseProvider)
class OpenAIProvider(BaseProvider):
    
    def __init__(self):
        super().__init__("openai")
        
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        # Create OpenAI async client
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            timeout=config.REQUEST_TIMEOUT_SECONDS
        )
    
    # Generate response from OpenAI model
    async def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
       
        start_time = time.time()
        
        try:
            # Send prompt to OpenAI Chat Completion API
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                # Control randomness of output
                temperature=kwargs.get("temperature", 0.7),
                # Limit maximum response tokens
                max_tokens=kwargs.get("max_tokens", 1000)
            )
            
            # Calculate latency
            latency = time.time() - start_time
            
            # Convert OpenAI response to standard format
            return self.normalize_response(response, model, latency)

        # Handle OpenAI rate limit error    
        except OpenAIRateLimitError as e:
            raise RateLimitError(f"OpenAI rate limit exceeded: {e}")
        except OpenAITimeoutError as e:
            raise TimeoutError(f"OpenAI request timed out: {e}")
        except Exception as e:
            raise ProviderError(f"OpenAI error: {e}")
    
    # Convert OpenAI response into common response format
    def normalize_response(self, response: Any, model: str, latency: float) -> Dict[str, Any]:
       
        # Get first response choice
        choice = response.choices[0]
        usage = response.usage
        
        # Return standardized response
        return {
            "text": choice.message.content,
            "tokens": usage.total_tokens,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "model": model,
            "provider": self.provider_name,
            "metadata": {
                "latency_seconds": round(latency, 2),
                "finish_reason": choice.finish_reason
            }
        }