# Changelog

All notable changes to the **Enterprise AI Gateway** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-11-21

### Added
- **Full-Stack Observability with Prometheus & Grafana (`docker-compose.yml`)**:
  - Expanded the Docker Compose orchestration to a **5-container enterprise stack**:
    1. `redis` (`redis:7-alpine`): Distributed caching backend.
    2. `litellm`: Unified multi-model routing proxy.
    3. `ai-gateway-app`: Core FastAPI & LangGraph gateway.
    4. `prometheus` (`prom/prometheus:latest`): Time-series metrics engine scraping gateway metrics at 5-second intervals on port `9090`.
    5. `grafana` (`grafana/grafana:latest`): Visualization portal with auto-provisioned dashboards on port `3000`.
- **Automated Grafana Provisioning (`grafana/provisioning/`)**:
  - **Datasource Provisioning (`grafana/provisioning/datasources/prometheus.yml`)**: Automatically registers the internal Prometheus service (`http://prometheus:9090`) as the default datasource on container launch.
  - **Dashboard Provisioning (`grafana/provisioning/dashboards/dashboard.yml`)**: Auto-loads dashboards from `/var/lib/grafana/dashboards` with zero manual UI setup.
- **Pre-Configured Enterprise AI Gateway Dashboard (`grafana/dashboards/ai-gateway-dashboard.json`)**:
  - Pre-built Grafana dashboard titled **"Enterprise AI Gateway Observability"** (`ai-gateway-overview`) with 5-second auto-refresh.
  - **Panel 1 - Total Requests & Guardrail Blocks**: Time-series breakdown of requests by HTTP status (`http_requests_total{handler="/chat"}`), tracking 2xx approvals vs. policy blocks.
  - **Panel 2 - Average Request Latency**: Real-time calculation of average gateway latency in seconds using rate quotients (`rate(http_request_duration_seconds_sum) / rate(...)`).
- **Prometheus Configuration (`prometheus.yml`)**:
  - Created root Prometheus scrape config targeting `ai-gateway-app:8000/metrics` with 5s evaluation interval.
- **Documentation**:
  - Embedded live Grafana telemetry dashboard screenshot (`grafana-dashboard.png`) into `README.md`.

---

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
  - Full microservices stack with three containerized services (`redis`, `litellm`, `ai-gateway-app`).
  - Configured service health check dependencies: LiteLLM waits for healthy Redis; AI Gateway waits for LiteLLM.
- **Production Multi-Stage Dockerfile (`Dockerfile`)**:
  - Multi-stage build with UV binary hydration and minimal runtime stage.
- **Distributed Redis Response Caching (`litellm_config.yaml`)**:
  - Migrated to distributed Redis cache with configurable TTL (`ttl: 3600`).
- **Dynamic Gateway Environment Configuration (`app/graph.py`)**:
  - Made LiteLLM proxy base URL dynamic via `os.getenv("LITELLM_BASE_URL", ...)`.
  - Dynamic master key injection via `os.getenv("LITELLM_MASTER_KEY", ...)`.

### Fixed
- Fixed missing `import os` in `app/graph.py`.
- Resolved conflicting cache type configuration in `litellm_config.yaml`.

---

## [0.3.0] - 2026-11-21

### Added
- **Automated Test Suite (`tests/test_gateway.py`)**:
  - Deterministic unit testing for PII regex redaction.
  - End-to-end integration test asserting prompt injection blocks.
  - Live LLM response quality test using `pytest.mark.skipif`.
- **Continuous Integration (CI) Workflow (`.github/workflows/ci.yml`)**:
  - GitHub Actions workflow triggering on `push` and `pull_request` to `main`.
- **Test Configuration & Dependencies**:
  - Added `pytest>=9.2.0` and `httpx>=0.28.1` to dependencies.

---

## [0.2.0] - 2026-11-21

### Added
- **LiteLLM Proxy & Router Integration (`litellm_config.yaml`)**:
  - Multi-model routing: Primary `groq/qwen/qwen3.8-27b`, Fallback `gemini/gemini-2.5-flash`.
  - Automated fallback routing policy with `num_retries: 2`.
  - In-memory local response caching.
- **LangChain OpenAI Interface (`app/graph.py`)**:
  - Integrated `langchain-openai` (`ChatOpenAI`) connecting LangGraph to the local LiteLLM Proxy endpoint.

---

## [0.1.0] - 2026-11-21

### Added
- **Initial Enterprise AI Gateway Release**:
  - FastAPI core service with `/chat` and Prometheus `/metrics`.
  - LangGraph `StateGraph` pipeline with input guard and LLM nodes.
  - Security guardrails for prompt injection and PII redaction (Aadhaar, PAN, Email, Phone).
  - Groq `qwen/qwen3.8-27b` provider integration.
