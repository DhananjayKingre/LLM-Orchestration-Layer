# basic system tests using pytest
import pytest
from intents.detector import detect_intent
from router.router import router
from tracking.usage import tracker
from tracking.cooldown import cooldown_manager

# test if intent detection works correctly
def test_intent_detection():
    
    assert detect_intent("write me some Python code") == "code_generation"
    assert detect_intent("explain how neural networks work") == "education"
    assert detect_intent("write an email to my boss") == "writing"
    assert detect_intent("translate this to Spanish") == "translation"
    assert detect_intent("summarize this article") == "summarization"
    assert detect_intent("hello there") == "general"

# test if model routing selects a valid provider and model
def test_model_routing():
   
    provider, model = router.select_model("code_generation")
    assert provider in ["openai", "anthropic", "mock_success"]
    assert model is not None

# test token usage tracking
def test_token_tracking():
    
    tracker.reset_usage()
    tracker.record_usage("test-model", 100)
    assert tracker.get_total_usage("test-model") == 100
    
    tracker.record_usage("test-model", 50)
    assert tracker.get_total_usage("test-model") == 150

# test cooldown functionality
def test_cooldown():
    
    cooldown_manager.clear_cooldown("test-model")
    assert not cooldown_manager.is_on_cooldown("test-model")
    
    cooldown_manager.trigger_cooldown("test-model", duration_seconds=5)
    assert cooldown_manager.is_on_cooldown("test-model")