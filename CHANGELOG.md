# Changelog

All notable changes to the **Enterprise AI Gateway** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-11-21

### Added
- **LiteLLM Proxy & Router Integration (`litellm_config.yaml`)**:
  - Implemented an enterprise multi-model routing layer with OpenAI-compatible endpoint on port `4000`.
  - Configured `enterprise-chat` as primary model backed by `groq/qwen/qwen3.8-27b`.
  - Configured `enterprise-chat-fallback` as secondary model backed by `gemini/gemini-2.5-flash`.
  - Automated fallback routing policy with `num_retries: 2` on rate limits, network timeouts, or upstream outages.
  - In-memory local response caching (`cache: true`, `type: local`) to eliminate redundant LLM calls and cut API costs.
- **LangChain OpenAI Interface (`app/graph.py`)**:
  - Integrated `langchain-openai` (`ChatOpenAI`) connecting LangGraph to the local LiteLLM Proxy endpoint (`http://localhost:4000/v1`).
- **Dependencies**:
  - Added `litellm[proxy]>=1.110.2` and `langchain-openai>=1.8.5` to `pyproject.toml` and `requirements.txt`.
- **Environment Configuration**:
  - Added support for `GEMINI_API_KEY` and `LITELLM_MASTER_KEY` to `.env` and `.env.example`.

### Changed
- **Agent Graph Pipeline (`app/graph.py`)**:
  - Redirected LLM execution node to route queries through LiteLLM Proxy rather than calling Groq directly.
- **Documentation (`README.md`)**:
  - Updated architecture diagram with LiteLLM proxy routing, multi-model failover, and response caching.
  - Added step-by-step instructions for running the LiteLLM proxy service alongside the FastAPI gateway.

---

## [0.1.0] - 2026-11-21

### Added
- **Initial Enterprise AI Gateway Release**:
  - **FastAPI Core Service (`app/main.py`)**: Asynchronous `/chat` endpoint with request validation via Pydantic (`ChatRequest`).
  - **LangGraph State Machine (`app/graph.py`)**: Stateful workflow execution (`AgentState`) featuring `input_guard_node`, `llm_node`, and `route_after_guard` conditional routing.
  - **Security Guardrails Engine (`app/guardrails.py`)**:
    - Real-time prompt injection heuristics detection (`ignore previous instructions`, `system prompt`, `jailbreak`).
    - Sensitive PII regex detection and in-place redaction for Indian Aadhaar cards, PAN cards, email addresses, and phone numbers.
  - **Observability & Telemetry**:
    - Integrated `prometheus-fastapi-instrumentator` with `/metrics` endpoint.
  - **Direct LLM Provider**:
    - Direct integration with Groq API (`ChatGroq`) using `qwen/qwen3.8-27b`.
  - **Project Scaffolding**:
    - Environment templates (`.env.example`), `.gitignore`, `pyproject.toml`, and `requirements.txt`.
