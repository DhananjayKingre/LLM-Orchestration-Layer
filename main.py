#FastAPI LLM Orchestration Layer
#Production-grade routing, fallback, and tracking system

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import time

# Import provider setup and custom error types
from providers import initialize_providers, get_provider, ProviderError, RateLimitError, TimeoutError
from intents.detector import detect_intent
from router.router import router
from tracking.usage import tracker
from tracking.cooldown import cooldown_manager
from config import config

# Create FastAPI application
app = FastAPI(
    title="LLM Orchestration Layer",
    description="Production-grade multi-provider LLM routing system",
    version="1.0.0"
)

# Allow requests from any frontend (React, Streamlit, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This runs automatically when the server starts
@app.on_event("startup")
async def startup_event():
    # Print startup message
    print("\n" + "="*60)
    print("🚀 Starting LLM Orchestration Layer")
    print("="*60)
    # Initialize all LLM providers (OpenAI, Groq, etc.)
    initialize_providers()
    print("="*60 + "\n")

# Request Model (input format)
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="User prompt text", min_length=1)
    preference: Optional[str] = Field(
        "balanced",
        description="Routing preference: cost, speed, quality, or balanced"
    )
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Temperature (0.0 - 1.0)")

# Response Model (output format)
class GenerateResponse(BaseModel):
    text: str
    model_used: str
    provider: str
    tokens_used: int
    intent: str
    metadata: Dict[str, Any]
    fallback_used: bool = False
    fallback_reason: Optional[str] = None

# Model usage statistics structure
class UsageStats(BaseModel):
    model: str
    total_tokens: int
    last_hour_tokens: int
    on_cooldown: bool
    cooldown_remaining_seconds: int

# Full system stats structure
class SystemStats(BaseModel):
    total_requests: int
    models: List[UsageStats]
    active_cooldowns: Dict[str, int]

# Main LLM generation endpoint
@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    
    # Generate LLM response with intelligent routing and fallback
    
    #1. Detect intent from prompt
    #2. Route to best available model
    #3. Try generation, fallback on failure
    #4. Track usage and check cooldown threshold
    #5. Return response
    
    # Record start time to measure latency
    start_time = time.time()
    
    # Step 1: Understand user intent
    intent = detect_intent(request.prompt)
    print(f"📋 Intent detected: {intent}")
    
    # Step 2: Choose best model based on intent + preference
    selection = router.select_model(intent, preference=request.preference)
    
    # If no model is available (all in cooldown)
    if not selection:
        raise HTTPException(
            status_code=503,
            detail="No models available - all are on cooldown"
        )
    
    provider_name, model_name = selection
    print(f"🎯 Selected: {provider_name}/{model_name}")
    
    # Step 3: Variables to track fallback behavior
    fallback_used = False
    fallback_reason = None
    tried_models = []
    
    # Get list of backup models
    fallback_chain = router.get_fallback_chain(intent, model_name)
    all_attempts = [(provider_name, model_name)] + fallback_chain
    
    last_error = None
    
    for attempt_provider, attempt_model in all_attempts:
        tried_models.append(attempt_model)
        
        try:
            print(f"🔄 Trying: {attempt_provider}/{attempt_model}")
            
            # Get provider
            provider = get_provider(attempt_provider)
            
            # Ask model to generate response
            result = await provider.generate(
                prompt=request.prompt,
                model=attempt_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # Step 4: Record token usage
            tracker.record_usage(
                model=attempt_model,
                tokens=result["tokens"],
                provider=attempt_provider
            )
            
            # Check cooldown threshold
            cooldown_triggered = cooldown_manager.check_and_trigger_cooldown(
                model=attempt_model,
                window_seconds=3600  # 1 hour window
            )
            
            if cooldown_triggered:
                print(f"❄️  Cooldown triggered for {attempt_model}")
            
            # If fallback model was used
            if attempt_model != model_name:
                fallback_used = True
                fallback_reason = f"Primary model failed: {str(last_error)[:100]}"
            
            # Calculate total latency
            total_latency = time.time() - start_time
            
            # Step 5: Return response
            return GenerateResponse(
                text=result["text"],
                model_used=attempt_model,
                provider=attempt_provider,
                tokens_used=result["tokens"],
                intent=intent,
                metadata={
                    **result["metadata"],
                    "total_latency_seconds": round(total_latency, 2),
                    "tried_models": tried_models,
                    "cooldown_triggered": cooldown_triggered
                },
                fallback_used=fallback_used,
                fallback_reason=fallback_reason
            )
            
        except RateLimitError as e:
            last_error = e
            print(f"⚠️  Rate limit hit on {attempt_model}: {e}")
            # Trigger immediate cooldown for rate-limited model
            cooldown_manager.trigger_cooldown(attempt_model, duration_seconds=600)
            continue
            
        except TimeoutError as e:
            last_error = e
            print(f"⏱️  Timeout on {attempt_model}: {e}")
            continue
            
        except ProviderError as e:
            last_error = e
            print(f"❌ Provider error on {attempt_model}: {e}")
            continue
            
        except Exception as e:
            last_error = e
            print(f"💥 Unexpected error on {attempt_model}: {e}")
            continue
    
    # If all models failed
    raise HTTPException(
        status_code=500,
        detail={
            "error": "All models failed",
            "tried_models": tried_models,
            "last_error": str(last_error)
        }
    )

# Get system statistics
@app.get("/stats", response_model=SystemStats)
async def get_stats():
    #Get system usage statistics
    
    all_usage = tracker.get_all_usage()
    
    # Build stats for each model
    model_stats = []
    for model, total_tokens in all_usage.items():
        # Skip provider aggregates
        if model.startswith("provider:"):
            continue
        
        model_stats.append(UsageStats(
            model=model,
            total_tokens=total_tokens,
            last_hour_tokens=tracker.get_usage_last_hour(model),
            on_cooldown=cooldown_manager.is_on_cooldown(model),
            cooldown_remaining_seconds=cooldown_manager.get_remaining_cooldown(model)
        ))
    
    # Get active cooldowns
    active_cooldowns = cooldown_manager.get_all_cooldowns()
    
    return SystemStats(
        total_requests=sum(all_usage.values()),
        models=model_stats,
        active_cooldowns=active_cooldowns
    )

# Health check endpoint (used by monitoring tools)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "providers_available": len(initialize_providers())
    }

# Reset system (mainly for testing)

@app.post("/reset")
async def reset_system():
    tracker.reset_usage()
    # Clear all cooldowns
    for model in list(cooldown_manager._cooldowns.keys()):
        cooldown_manager.clear_cooldown(model)
    
    return {"message": "System reset successful"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)





