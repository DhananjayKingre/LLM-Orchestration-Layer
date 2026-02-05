#Intelligent model routing with fallback support

from typing import List, Tuple, Optional, Dict
from config import config
from tracking.cooldown import cooldown_manager
from tracking.usage import tracker

# This class decides which model should handle a request
class ModelRouter:
    
    #Route requests to appropriate models based on Intent ,Model capabilities , Cost/latency/quality preferences, Cooldown status
    
    
    def __init__(self):
        self.intent_routing = config.INTENT_ROUTING
        self.model_config = config.MODEL_CONFIG
        
        # Store fallback history (helps avoid repeating same failures)
        self._fallback_history: Dict[str, List[str]] = {}
    
    # Choose the best model for a request
    def select_model(
        self, 
        intent: str, 
        preference: str = "balanced",
        excluded_models: Optional[List[str]] = None
    ) -> Optional[Tuple[str, str]]:
        
        # Get candidate models for this intent
        candidate_models = self.intent_routing.get(intent, ["gpt-3.5-turbo"])
        
        # Remove models that should not be used
        if excluded_models:
            candidate_models = [
                m for m in candidate_models 
                if m not in excluded_models
            ]
        
        # Remove models that are in cooldown
        available_models = [
            model for model in candidate_models
            if not cooldown_manager.is_on_cooldown(model)
        ]
        
        # If no models are available
        if not available_models:
            return None
        
        # Sort models based on user preference
        if preference == "cost":
            # Lowest cost first
            available_models.sort(
                key=lambda m: self.model_config[m]["cost_per_1k"]
            )
        elif preference == "speed":
            # Fastest first
            speed_order = {"very_fast": 0, "fast": 1, "medium": 2, "slow": 3}
            available_models.sort(
                key=lambda m: speed_order.get(
                    self.model_config[m]["speed"], 99
                )
            )
        elif preference == "quality":
            # Highest quality first
            quality_order = {"high": 0, "medium": 1, "low": 2}
            available_models.sort(
                key=lambda m: quality_order.get(
                    self.model_config[m]["quality"], 99
                )
            )
        else:  # balanced
            # Use the order defined in INTENT_ROUTING
            pass
        
        # Select first available model
        selected_model = available_models[0]
        provider = self.model_config[selected_model]["provider"]
        
        return (provider, selected_model)
    
    # Get backup models if primary model fails
    def get_fallback_chain(
        self, 
        intent: str, 
        failed_model: str,
        max_fallbacks: int = 3
    ) -> List[Tuple[str, str]]:
       
        # Get all candidate models
        candidate_models = self.intent_routing.get(intent, ["gpt-3.5-turbo"])
        
        # Remove the model that already failed
        fallback_models = [m for m in candidate_models if m != failed_model]
        
        # Remove models that are in cooldown
        fallback_models = [
            m for m in fallback_models
            if not cooldown_manager.is_on_cooldown(m)
        ]
        
        # Limit number of fallback attempts
        fallback_models = fallback_models[:max_fallbacks]
        
        # Convert model names into (provider, model) pairs
        result = []
        for model in fallback_models:
            provider = self.model_config[model]["provider"]
            result.append((provider, model))
        
        return result
    
    # Get full configuration of a model
    def get_model_info(self, model: str) -> Dict:
        
        return self.model_config.get(model, {})
    
    # Check if a model is available
    def is_model_available(self, model: str) -> bool:
       
        return not cooldown_manager.is_on_cooldown(model)

# Create one global router object
router = ModelRouter()

# Backward compatibility
MODEL_MAP = config.INTENT_ROUTING

# Old function (kept for compatibility)
def get_models(intent: str) -> List[str]:
    """Legacy function"""
    return MODEL_MAP.get(intent, ["gpt-3.5-turbo"])



