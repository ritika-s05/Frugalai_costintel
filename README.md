# Frugal AI — LLM Cost Intelligence

**An AI gateway for cost-aware model routing, semantic caching, request-level cost tracking, and operational visibility.**

Frugal AI explores a practical engineering question: *Does every AI request need to run on the same model, and how can we measure the cost of that decision?* It provides an OpenAI-style chat-completions endpoint backed by routing, a per-request cost guard, a semantic cache, provider execution, and SQL-backed telemetry. A React dashboard surfaces usage and savings metrics, while an interactive simulator illustrates cache-hit and cache-miss execution paths.

> **Project status:** Active development / portfolio project. The interactive infrastructure simulator is illustrative: it does not invoke model providers or change the live analytics database. Production readiness, provider configuration, and measured savings should be evaluated independently before deployment.

## What it does

- **SmartRouter:** selects an execution model for incoming chat requests.
- **TokenGuard:** checks an estimated request cost against a configured per-request limit before execution.
- **Semantic cache:** attempts to reuse eligible responses and skip provider execution on cache hits. The current implementation uses a shared application-process cache; it is not described as a persistent distributed cache.
- **Provider gateway:** executes cache misses through the configured model-provider integration and returns a chat-completions-style response.
- **Cost telemetry:** stores request-level estimated/actual cost, baseline cost, savings, routing status, cache-hit status, and provider latency in PostgreSQL.
- **Analytics dashboard:** fetches live summary metrics from the FastAPI backend.
- **Interactive architecture simulator:** visually demonstrates request progression through TokenGuard, SmartRouter, caching, provider/cached response, and telemetry. Simulation results are not actual API calls.

## Architecture

```text
                        Incoming chat request
                                 |
                         FastAPI /v1 API
                                 |
                           SmartRouter
                                 |
                            TokenGuard
                       (cost-budget check)
                                 |
                           Semantic cache
                            /          \
                         HIT            MISS
                          |               |
                   Cached response    AI provider
                          |               |
                          +-------+-------+
                                  |
                          Request telemetry
                                  |
                       PostgreSQL + SQLAlchemy
                                  |
                       GET /analytics/summary
                                  |
                         React analytics UI
```

The flow above describes the backend conceptually. The frontend simulator demonstrates the same cache-hit/cache-miss distinction but operates independently of real gateway execution.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Backend | Python, FastAPI, Pydantic |
| AI gateway | Provider adapters, LiteLLM/OpenAI-related dependencies, routing and caching services |
| Persistence | PostgreSQL, SQLAlchemy, Alembic |
| Frontend | React, TypeScript, Vite |
| UI | Motion, Lucide icons, Recharts |
| Configuration | Environment variables and Pydantic Settings |

## Repository layout

```text
Frugalai_costintel/
├── backend/
│   ├── app/
│   │   ├── api/             # Chat-completions and analytics routes
│   │   ├── core/            # Configuration and exceptions
│   │   ├── database/        # Database dependencies
│   │   ├── models/          # Persisted request records
│   │   ├── providers/       # Provider integrations
│   │   ├── schemas/         # Request/response models
│   │   └── services/        # Gateway, routing, cache, guard, telemetry
│   └── requirements.txt
├── frontend/
│   └── react/               # React/Vite application
└── README.md
```

## Run locally

### Prerequisites

- Python and Node.js compatible with the checked-in dependencies
- A PostgreSQL database (a hosted PostgreSQL instance such as Supabase can be used)
- API credentials for the model providers configured in the backend

### 1. Clone and install backend dependencies

```bash
 git clone https://github.com/ritika-s05/Frugalai_costintel.git
 cd Frugalai_costintel
 python3 -m venv .venv
 source .venv/bin/activate
 pip install -r backend/requirements.txt
```

Create `backend/.env` with the settings expected by `backend/app/core/config.py`:

```dotenv
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

The current settings schema requires these variables to be present; actual provider usage depends on the selected model and provider configuration. **Never commit real credentials.** Run the project's Alembic migrations against your configured database before starting the API.

```bash
cd backend
# Apply the migrations configured in your local Alembic setup.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

The backend should expose:

- Health: `http://127.0.0.1:8002/health`
- Interactive API documentation: `http://127.0.0.1:8002/docs`
- Analytics: `http://127.0.0.1:8002/analytics/summary`

**Note:** If your Python environment reports a missing `uvicorn` module, install `uvicorn` explicitly. The currently checked-in backend requirements list `unicorn`, not `uvicorn`; that dependency entry should be corrected and verified separately.

### 2. Start the React frontend

Open a second terminal:

```bash
cd Frugalai_costintel/frontend/react
npm install
npm run dev
```

The Vite development server is configured to use port **5174**. The frontend defaults to `http://127.0.0.1:8002` for the API; override it with `VITE_API_BASE_URL` when necessary. Keep the backend and frontend running in separate terminals.

To verify a production build:

```bash
npm run build
```

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `POST` | `/v1/chat/completions` | Route and execute a chat-completions request |
| `GET` | `/analytics/summary` | Aggregate recorded request and cost metrics |

Example chat request (requires working provider credentials and database configuration):

```bash
curl -X POST http://127.0.0.1:8002/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "YOUR_CONFIGURED_MODEL",
    "messages": [{"role": "user", "content": "Explain semantic caching."}],
    "temperature": 0.7
  }'
```

Replace `YOUR_CONFIGURED_MODEL` with a model supported by the current provider/router implementation.

## Understanding the metrics

The analytics endpoint includes total requests, actual cost, recorded baseline cost, recorded savings, savings percentage, cache-hit rate, routing rate, and average non-cache provider latency. **Interpret savings with the recorded baseline cohort in mind:** requests without a baseline can still contribute to total actual cost. Do not subtract the displayed total actual cost from the displayed baseline cost and assume both represent identical request populations.

Results depend on request mix, model pricing assumptions, cache behavior, and the available baseline records. This README deliberately avoids presenting sample-run savings as a production benchmark.

## Current scope and next steps

- [x] FastAPI gateway and chat-completions endpoint
- [x] Cost guard, routing, semantic-cache path, and request logging
- [x] PostgreSQL-backed analytics summary
- [x] React analytics interface connected to the backend
- [x] Interactive cache-hit/cache-miss infrastructure simulator
- [ ] Document and automate reproducible end-to-end tests and evaluation runs
- [ ] Validate dependency installation and database migration instructions on a clean environment
- [ ] Add deployment configuration, authentication, and production observability as appropriate

## Security and development notes

Use environment variables for secrets and keep `.env` out of version control. The development CORS configuration permits selected localhost frontend ports and is not a production security configuration. The demo simulator should not be mistaken for a live request trace.

---

Built as a software engineering and AI infrastructure portfolio project focused on practical LLM cost optimization and transparent measurement.
