# LLM Orchestration Layer

**LLM Orchestration Layer** is a production-grade system for managing multiple large language model (LLM) providers. It intelligently routes user requests to the best model based on **intent**, applies **fallbacks** when a model fails, tracks **token usage**, and enforces **cooldowns** for overused models.  

This system is designed for real-world applications where multiple providers (OpenAI, Anthropic, Mock) are used, making LLM integration **reliable, cost-effective, and efficient**.

---

## Project Overview

The project provides:

- Multi-provider LLM support with unified interface.
- Rule-based intent detection to route requests to the right model.
- Automatic fallback if the primary model fails.
- Token usage tracking with time windows (last hour, last minute).
- Cooldown mechanism to prevent overloading a model.
- Thread-safe concurrent request handling.
- Clear error handling and normalized responses.

---

## Techniques Used

- **FastAPI** for the API server (async-ready for concurrent requests).  
- **Async LLM calls** to providers (OpenAI, Anthropic, Mock) for efficient I/O.  
- **Rule-based Intent Detection** using keyword matching.  
- **Intelligent Model Routing** based on intent, user preference (`cost`, `speed`, `quality`), and model availability.  
- **Fallback System** to try alternative models if a model fails or times out.  
- **Token Usage Tracking** with rolling time windows.  
- **Cooldown Management** to automatically block models exceeding thresholds.  
- **Thread-safe coding** using `Lock` for concurrent requests.

---

## Models and Keys Used

- **OpenAI GPT Models**:  
  - `gpt-4` (high quality, slow, expensive)  
  - `gpt-3.5-turbo` (medium quality, fast, low cost)  
  - Requires `OPENAI_API_KEY` in `.env`.

- **Anthropic Claude Models**:  
  - `claude-sonnet-4` (high quality, medium speed)  
  - `claude-haiku-4` (medium quality, very fast)  
  - Requires `ANTHROPIC_API_KEY` in `.env` (optional).

- **Mock Providers** (for testing without API usage):  
  - `MockSuccessProvider` → always succeeds.  
  - `MockFailureProvider` → always fails.  
  - `MockRateLimitProvider` → simulates rate limits.

---

## Key Features

1. **Multi-provider support**: OpenAI, Anthropic, and Mock for testing.  
2. **Intent detection**: Classifies user prompts into `code_generation`, `education`, `writing`, `translation`, `summarization`, or `general`.  
3. **Intelligent routing**: Routes requests to best model based on intent + user preference + cooldown status.  
4. **Fallback mechanism**: Tries alternative models if primary fails.  
5. **Token usage tracking**: Monitors token consumption per model and provider.  
6. **Cooldown enforcement**: Automatically blocks overused models to prevent throttling.  
7. **Thread-safe**: Safe for concurrent requests.  
8. **Error handling**: Normalizes provider errors (rate limits, timeouts, invalid requests).

---

## Project Workflow

1. **User Request** → `/generate` endpoint.  
2. **Intent Detection** → Determine the type of request (e.g., code, writing).  
3. **Model Selection** → Route to the best model according to intent, user preference, and cooldown status.  
4. **Provider Call** → Call the selected LLM asynchronously.  
5. **Fallback** → If primary fails, try fallback models.  
6. **Usage Tracking** → Record tokens consumed by each model.  
7. **Cooldown Check** → Trigger cooldown if token usage exceeds threshold.  
8. **Response** → Return the generated text with metadata.

**ASCII Flow Diagram:**

```
User Request
     |
     v
Intent Detection (rule-based)
     |
     v
Model Selection (preference + cooldown)
     |
     v
Provider Call (async + timeout)
     |
     v
Fallback (if model fails)
     |
     v
Token Usage Tracking
     |
     v
Cooldown Check
     |
     v
Response Returned
```

---

## Code File Flow

| File/Folder | Purpose |
|-------------|---------|
| `main.py` | FastAPI server and endpoints `/generate`, `/stats`, `/health`, `/reset`. |
| `config.py` | Central configuration: API keys, model info, routing rules, thresholds. |
| `providers/` | LLM provider implementations: OpenAI, Anthropic, Mock. |
| `providers/base.py` | BaseProvider class with unified interface and error handling. |
| `providers/openai_provider.py` | Async OpenAI provider wrapper. |
| `providers/anthropic_provider.py` | Async Anthropic provider wrapper. |
| `providers/mock_provider.py` | Mock providers for testing without real API calls. |
| `intents/detector.py` | Rule-based intent detection. |
| `intents/__init__.py` | Expose detector and helper functions. |
| `router/router.py` | Intelligent model routing and fallback system. |
| `tracking/usage.py` | TokenTracker class for usage monitoring. |
| `tracking/cooldown.py` | CooldownManager class to manage overused models. |
| `tests/test_system.py` | Basic system tests: intent, routing, token usage, cooldown. |

---

## File Structure (Local)

```
D:\llm_orchestrator\
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── config.py
├── main.py
│
├── providers/
│   ├── __init__.py
│   ├── base.py
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   └── mock_provider.py
│
├── intents/
│   ├── __init__.py
│   └── detector.py
│
├── router/
│   ├── __init__.py
│   └── router.py
│
├── tracking/
│   ├── __init__.py
│   ├── usage.py
│   └── cooldown.py
│
└── tests/
    └── test_system.py
```

---

## Running the Project

1. **Create Virtual Environment**

```bash
python -m venv venv
```

2. **Activate Virtual Environment**

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

Create `.env` file:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here (optional)
TOKEN_COOLDOWN_THRESHOLD=5000
COOLDOWN_DURATION_SECONDS=300
```

5. **Run the Server**

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`.

6. **Test Endpoints**

**Generate LLM response:**

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum computing in simple terms"}'
```

**Get stats:**

```bash
curl "http://localhost:8000/stats"
```

**Health check:**

```bash
curl "http://localhost:8000/health"
```

7. **Run Tests**

```bash
pytest tests/
```

---

## License

MIT License

