
#Intent classification module
#Deterministic, rule-based intent detection

from typing import Dict, List

# This class decides what the user wants (coding, writing, learning, etc.)
class IntentDetector:
    # Keywords for each type of user request
    # If a word from the list appears in prompt, that intent gets score
    
    # Intent definitions with keywords
    INTENT_KEYWORDS = {
        "code_generation": [
            "code", "program", "function", "class", "script",
            "python", "javascript", "java", "implement", "debug",
            "algorithm", "refactor", "write code"
        ],
        "education": [
            "explain", "teach", "learn", "understand", "what is",
            "how does", "tutorial", "lesson", "clarify", "define"
        ],
        "writing": [
            "write", "email", "letter", "article", "essay",
            "blog", "post", "content", "draft", "compose"
        ],
        "translation": [
            "translate", "translation", "convert to", "in spanish",
            "in french", "in german", "language"
        ],
        "summarization": [
            "summarize", "summary", "tldr", "brief", "condense",
            "key points", "main idea", "overview"
        ]
    }
    
    # This function checks the prompt and decides intent
    def detect(self, prompt: str) -> str:

       # Convert text to lowercase for easy matching

        prompt_lower = prompt.lower()
        
        # Store score for each intent
        scores: Dict[str, int] = {}
        
        # Check how many keywords match for each intent
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in prompt_lower:
                    score += 1
            scores[intent] = score
        
        # Get highest scoring intent
        max_score = max(scores.values())
        
        if max_score == 0:
            return "general"
        
        # Return intent with highest score
        for intent, score in scores.items():
            if score == max_score:
                return intent
        
        return "general"
    
    # This function tells how confident we are about detected intent
    def get_confidence(self, prompt: str, intent: str) -> float:
       
        prompt_lower = prompt.lower()
        
        # General intent has medium confidence
        if intent == "general":
            return 0.5
        
        keywords = self.INTENT_KEYWORDS.get(intent, [])
        # Count matching keywords
        matches = sum(1 for kw in keywords if kw in prompt_lower)
        
        if not keywords:
            return 0.0
        
        # Confidence = matched keywords / total keywords (max 1.0)
        return min(matches / len(keywords), 1.0)

# Create one global detector object
detector = IntentDetector()

# Simple helper function so other files can call detect_intent()
def detect_intent(prompt: str) -> str:
    
    return detector.detect(prompt)











