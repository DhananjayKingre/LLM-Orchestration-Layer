#Token usage tracking with time-window support

import time
from typing import Dict, List, Tuple
from collections import defaultdict
# Lock makes this safe when many requests happen at same time
from threading import Lock

# This class tracks how many tokens each model uses
class TokenTracker:
    
    
    def __init__(self):
        # Store token usage with timestamp
        self._usage: Dict[str, List[Tuple[float, int]]] = defaultdict(list)
        self._lock = Lock()
        
        # Store total tokens used per model (all time)
        self._total_usage: Dict[str, int] = defaultdict(int)
    
    # Save token usage when a model generates output
    def record_usage(self, model: str, tokens: int, provider: str = None):
        
        with self._lock:
            timestamp = time.time()
            
            # Save usage for model with time
            self._usage[model].append((timestamp, tokens))
            
           # Increase total token count
            self._total_usage[model] += tokens
            
            # If provider specified, track provider totals too
            if provider:
                provider_key = f"provider:{provider}"
                self._usage[provider_key].append((timestamp, tokens))
                self._total_usage[provider_key] += tokens
    
    # Get tokens used in a recent time window (like last hour)
    def get_usage_in_window(self, model: str, window_seconds: int = 3600) -> int:
        
        with self._lock:
            if model not in self._usage:
                return 0
            
            current_time = time.time()
            cutoff_time = current_time - window_seconds
            
            # Count only tokens inside the time window
            total = sum(
                tokens 
                for timestamp, tokens in self._usage[model]
                if timestamp >= cutoff_time
            )
            
            # Remove very old entries to save memory
            cleanup_cutoff = current_time - (window_seconds * 2)
            self._usage[model] = [
                (ts, tok) for ts, tok in self._usage[model]
                if ts >= cleanup_cutoff
            ]
            
            return total
    
    # Get total tokens used by a model (from start)
    def get_total_usage(self, model: str) -> int:
       
        with self._lock:
            return self._total_usage.get(model, 0)
    
    # Get total usage for all models
    def get_all_usage(self) -> Dict[str, int]:
        
        with self._lock:
            return dict(self._total_usage)
    
    # Shortcut to get last hour usage
    def get_usage_last_hour(self, model: str) -> int:
       
        return self.get_usage_in_window(model, window_seconds=3600)
    
    # Shortcut to get last minute usage
    def get_usage_last_minute(self, model: str) -> int:
       
        return self.get_usage_in_window(model, window_seconds=60)
    
    # Reset tracking data
    def reset_usage(self, model: str = None):
        
        with self._lock:
            if model:
                self._usage.pop(model, None)
                self._total_usage.pop(model, None)
            else:
                self._usage.clear()
                self._total_usage.clear()

# Create one global tracker object
tracker = TokenTracker()

# Old function name (still works)
def record_usage(model: str, tokens: int):
    
    tracker.record_usage(model, tokens)

# Old function name (still works)
def get_usage(model: str) -> int:
    
    return tracker.get_total_usage(model)


