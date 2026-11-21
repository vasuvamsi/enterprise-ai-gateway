# Changelog

All notable changes to the **Enterprise AI Gateway** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-11-21

### Changed
- **Unified Python 3.14 Docker Environment (`Dockerfile`)**:
  - Upgraded both the builder and final runtime stages from `python:3.12-slim` to `python:3.14-slim`, ensuring 100% version alignment with `.python-version` and `pyproject.toml` (`>=3.14`).
  - Builder stage installs `uv` directly using `pip install --no-cache-dir uv` and targets Python 3.14 explicitly with `uv sync --python 3.14 --locked --no-install-project --no-dev`.
- **Shared Unified Image for LiteLLM Service (`docker-compose.yml`)**:
  - Replaced third-party `image: ghcr.io/berriai/litellm:main-stable` with the project's own unified local build (`build: .`).
  - Updated LiteLLM container command to run via the local Python package entry point: `["python", "-c", "from litellm.proxy.proxy_cli import run_server; run_server()", "--config", "/app/config.yaml", "--port", "4000"]`.
  - Reuses a single cached multi-stage Docker build across both gateway microservices, saving disk space and eliminating external registry pull delays.

---

## [0.4.0] - 2026-11-21

### Added
- **Multi-Container Docker Orchestration (`docker-compose.yml`)**:
  - Full microservices stack with three containerized services:
    1. `redis` (`redis:7-alpine`): Distributed caching backend with automated health check probe (`redis-cli ping`).
    2. `litellm`: High-availability AI routing proxy on port `4000`, connected to Redis for shared response caching.
    3. `ai-gateway-app`: Gateway application container built from local `Dockerfile`, exposing port `8000`.
  - Configured service health check dependencies: LiteLLM waits for healthy Redis; AI Gateway waits for LiteLLM.
- **Production Multi-Stage Dockerfile (`Dockerfile`)**:
  - Optimized multi-stage build.
  - UV binary extraction for fast locked dependency resolution (`uv sync --locked --no-install-project --no-dev`).
  - Lean final runtime stage containing only the virtual environment and application code.
- **Distributed Redis Response Caching (`litellm_config.yaml`)**:
  - Migrated from in-process local memory cache to distributed Redis cache with configurable TTL (`ttl: 3600`).
  - Added environment variable routing for `REDIS_HOST` and `REDIS_PORT`.
- **Dynamic Gateway Environment Configuration (`app/graph.py`)**:
  - Made LiteLLM proxy base URL dynamic via `os.getenv("LITELLM_BASE_URL", "http://localhost:4000/v1")` enabling seamless operation both locally and in Docker networks (`http://litellm:4000/v1`).
  - Dynamic master key injection via `os.getenv("LITELLM_MASTER_KEY", ...)`.

### Fixed
- Fixed missing `import os` in `app/graph.py` required for environment variable lookups.
- Resolved conflicting cache type configuration in `litellm_config.yaml` to ensure Redis distributed caching is active.

---

## [0.3.0] - 2026-11-21

### Added
- **Automated Test Suite (`tests/test_gateway.py`)**:
  - Deterministic unit testing for PII regex detection and redaction (Email, Indian Phone, and PAN) without external network dependencies (`test_pii_redaction_deterministic`).
  - End-to-end integration test asserting that prompt injection attacks are intercepted at the `/chat` endpoint and return security policy violations (`test_prompt_injection_blocked_at_api`).
  - Live LLM response quality test using `pytest.mark.skipif` to conditionally run only when `GROQ_API_KEY` is present (`test_live_gateway_response_quality`).
  - Package marker `tests/__init__.py`.
- **Continuous Integration (CI) Workflow (`.github/workflows/ci.yml`)**:
  - GitHub Actions workflow triggering on `push` and `pull_request` targeting the `main` branch.
  - Setup using `astral-sh/setup-uv@v4` for fast locked dependency hydration (`uv sync --frozen`).
  - Automated security, guardrail, and quality test execution via `uv run pytest -v`.
- **Test Configuration & Dependencies**:
  - Added `pytest>=9.2.0` and `httpx>=0.28.1` (required for FastAPI `TestClient`) to `pyproject.toml` and `requirements.txt`.
  - Configured `[tool.pytest.ini_options]` with `pythonpath = ["."]` in `pyproject.toml` for root-relative test imports.

---

## [0.2.0] - 2026-11-21

### Added
- **LiteLLM Proxy & Router Integration (`litellm_config.yaml`)**:
  - Implemented an enterprise multi-model routing layer with OpenAI-compatible endpoint on port `4000`.
  - Configured `enterprise-chat` as primary model backed by `groq/qwen/qwen3.8-27b`.
  - Configured `enterprise-chat-fallback` as secondary model backed by `gemini/gemini-2.5-flash`.
  - Automated fallback routing policy with `num_retries: 2` on rate limits, network timeouts, or upstream outages.
  - In-memory local response caching to eliminate redundant LLM calls and cut API costs.
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
