#Cooldown management for overused models
# Used to get current time

import time
from typing import Dict, Optional
from threading import Lock
from .usage import tracker

# This class controls cooldown for models when they are overused
class CooldownManager:
    
    #Manage model cooldowns based on token usage thresholds
    #Thread-safe implementation
    
    
    def __init__(
        self, 
        token_tracker=None,
        threshold: int = 5000,
        duration_seconds: int = 300
    ):
        
        #token_tracker: TokenTracker instance (uses global if None)
        #threshold: Token threshold for triggering cooldown
        #duration_seconds: How long cooldown lasts (default: 5 minutes)
        
        self.token_tracker = token_tracker or tracker
        self.threshold = threshold
        self.duration_seconds = duration_seconds
        
        # Store cooldown expiry times: {model_name: expiry_timestamp}
        self._cooldowns: Dict[str, float] = {}
        self._lock = Lock()
        
        # Statistics
        self._cooldown_count: Dict[str, int] = {}
    
    # Check if a model is currently in cooldown
    def is_on_cooldown(self, model: str) -> bool:
        
        with self._lock:
            if model not in self._cooldowns:
                return False
            
            expiry_time = self._cooldowns[model]
            current_time = time.time()
            
            # Check if cooldown has expired
            if current_time >= expiry_time:
                # Cooldown expired, remove it
                del self._cooldowns[model]
                return False
            
            return True
    
    # Manually put a model into cooldown
    def trigger_cooldown(self, model: str, duration_seconds: Optional[int] = None):
        
        # Use custom duration or default
        duration = duration_seconds or self.duration_seconds
        
        with self._lock:
            expiry_time = time.time() + duration
            self._cooldowns[model] = expiry_time
            
            # Increase cooldown counter for this model
            self._cooldown_count[model] = self._cooldown_count.get(model, 0) + 1
    
    # Automatically check usage and trigger cooldown if needed
    def check_and_trigger_cooldown(self, model: str, window_seconds: int = 3600) -> bool:
       
        # Get token usage in last window (like last hour)
        usage = self.token_tracker.get_usage_in_window(model, window_seconds)
        
        # If usage crossed threshold, start cooldown
        if usage >= self.threshold:
            self.trigger_cooldown(model)
            return True
        
        return False
    
    # Get how many seconds are left in cooldown
    def get_remaining_cooldown(self, model: str) -> int:
       
        with self._lock:
            if model not in self._cooldowns:
                return 0
            
            expiry_time = self._cooldowns[model]
            remaining = int(expiry_time - time.time())
            
            # Never return negative values
            return max(0, remaining)
    
    # Manually remove cooldown for a model
    def clear_cooldown(self, model: str):
        
        with self._lock:
            self._cooldowns.pop(model, None)
    
    # Get all models that are in cooldown right now
    def get_all_cooldowns(self) -> Dict[str, int]:
        
        with self._lock:
            current_time = time.time()
            
            result = {}
            for model, expiry_time in self._cooldowns.items():
                remaining = int(expiry_time - current_time)
                if remaining > 0:
                    result[model] = remaining
            
            return result
    
    # Get how many times cooldown happened for each model
    def get_statistics(self) -> Dict[str, int]:
       
        with self._lock:
            return dict(self._cooldown_count)

# Create global cooldown manager using values from config
from config import config
cooldown_manager = CooldownManager(
    threshold=config.TOKEN_COOLDOWN_THRESHOLD,
    duration_seconds=config.COOLDOWN_DURATION_SECONDS
)

# Backward compatibility functions
# Old dictionary kept for compatibility (not used directly)
cooldown = {}

# Old function name support
def is_on_cooldown(model: str) -> bool:
    
    return cooldown_manager.is_on_cooldown(model)

def set_cooldown(model: str, seconds: int = 60):
    
    cooldown_manager.trigger_cooldown(model, seconds)












