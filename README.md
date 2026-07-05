<div align="center">

# Owe

### AI-powered civic intelligence for neighborhood resilience.

*Inspired by T. M. Scanlon's moral philosophy, and his book 'What We Owe to Each Other'.*

[![Cloud Run](https://img.shields.io/badge/deployed-Cloud%20Run-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/run)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/frontend-React-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![BigQuery](https://img.shields.io/badge/data-BigQuery-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/bigquery)
[![Gemini](https://img.shields.io/badge/AI-Gemini%20API-8E44AD?logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e.svg)](./LICENSE)

</div>

---

## What is Owe?

Modern cities generate enormous amounts of civic data — accessibility incidents, waterlogging complaints, transit delays, air quality drops — and do almost nothing human with it.

Smart city platforms turn neighborhoods into spreadsheets. Social networks turn local concerns into fuel for outrage. Neither translates civic friction into **community solidarity**.

Owe is a different kind of civic platform. It aggregates fragmented neighborhood signals, synthesizes them with AI, and surfaces them as grounded, actionable **missions of mutual support** — framed not as charity, not as gamification, but as the simple obligations we owe to each other as neighbors in a shared locality.

It is calm. It is specific. It focuses on Kolkata.

---

## The Philosophy

> *"What we owe to each other is not charity. It is reasonable recognition."*  
> — T. M. Scanlon, **What We Owe to Each Other**

Owe is built on a principle called **civic reciprocity**: the idea that when a neighbor's access to the street, to safety, or to basic wellbeing is compromised, other neighbors have a soft obligation — not legal, not gamified, but moral — to act.

We deliberately reject:
- **Leaderboards** and points that reduce solidarity to competition.
- **Outrage feeds** that surface grievance without resolution.
- **Corporate volunteer language** that makes small acts feel bureaucratic.

Instead, every surface in Owe answers three questions:
1. What is happening in this neighborhood right now?
2. Who is being affected, and why does it matter?
3. What can I, as a neighbor, actually do?

---

## Product Overview

Owe has four core surfaces:

| Surface | Description |
|---|---|
| **Daily Brief** | A real-time overview of collective neighborhood wellness — pulse score, friction points, open missions, and emerging civic signals from the past 48 hours. |
| **Community Momentum** | A timeline of resolved issues, volunteer interventions, and positive recovery milestones. Designed to foster hope, not just urgency. |
| **Community Missions** | Story-driven mission cards explaining exactly why a specific situation matters, who it affects, and what action is needed. Deterministically assembled from real civic data. |
| **Civic AI Chat** | A conversational assistant that explains the logic behind its observations using grounded data markers, written in a calm, observant, and unhurried tone. |

---

## Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Client Browser                            │
│              React SPA (Vite + TailwindCSS)                  │
│       Dashboard │ Missions │ Chat │ Community Feed           │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP / JSON
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Server                            │
│                      (Port 8080)                             │
│  /api/health  /api/brief  /api/missions  /api/chat           │
│  /api/debug/bigquery  /api/debug/gemini                      │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐        ┌──────────────────────────────┐
│    AIService        │        │   Static File Router         │
│  ai_service.py      │        │   Serves /frontend/dist      │
│  Hybrid Pipeline    │        │   SPA catch-all to index.html│
└──────┬──────────────┘        └──────────────────────────────┘
       │
       ├──────────────────────────┐
       ▼                          ▼
┌──────────────┐        ┌─────────────────────────────────────┐
│ GeminiClient │        │          BigQueryService            │
│ gemini_client│        │       bigquery_service.py           │
│ .py          │        │  Parallel ThreadPoolExecutor fetches│
│ Enrichment   │        │  60-second in-memory cache          │
│ Only         │        │  civic_events, transport_density,   │
└──────────────┘        │  environmental_stress,              │
                        │  accessibility_incidents,           │
                        │  community_sentiment,               │
                        │  community_missions                 │
                        └─────────────────────────────────────┘
```

### Frontend ↔ Backend Communication

| Environment | Frontend | Backend | Routing |
|---|---|---|---|
| **Local Dev** | `localhost:5173` (Vite) | `localhost:8000` (uvicorn) | Vite proxy forwards `/api/*` to `:8000` |
| **Production** | Same container | Port `8080` | FastAPI serves `/dist` static files + SPA catch-all |

In production, the entire application ships as **a single Docker container**. FastAPI serves both the API and the compiled React assets. There is no separate web server or CDN required.

---

## The Hybrid AI Architecture

This is the most important section. Understanding this design is the key to understanding Owe's technical philosophy.

### Why We Don't Ask Gemini to Generate the Whole Page

The naive approach — and our initial implementation — asked Gemini to generate a complete, nested JSON array representing the entire mission feed or dashboard payload in one shot. It looked like this:

```
BigQuery → Context → Gemini → Giant JSON blob → Frontend
```

This failed for a fundamental reason: **language models have token limits**. When generating 10-15 missions, each with multiple structured fields, the output would hit `FINISH_REASON: MAX_TOKENS` mid-string. The JSON parser received a truncated blob. Parsing failed silently. The frontend showed empty cards.

We also tried more elaborate JSON extraction, regex cleaning of trailing commas, and retry logic. These were all patches on a structurally incorrect architecture.

### The Correct Mental Model

Think of it this way:

> A novelist can write beautifully. But you wouldn't ask a novelist to also typeset the book, design the cover, and organize the chapters. Those are separate jobs.

BigQuery is the database. It knows the facts: the neighborhood, the category, the urgency level, the affected group, the timestamp. These structural facts should **never** depend on a language model. They exist in the database and belong in the payload exactly as they are.

Gemini is the writer. It excels at one thing: understanding a situation and producing a sentence or two of human-centered reasoning. This is precisely what "Why It Matters" and "Action Guidance" require.

### The Hybrid Architecture

```
                    BigQuery
                       │
                       ▼
         ┌─────────────────────────┐
         │  Deterministic Python   │
         │  Assembly               │
         │                         │
         │  title       ← BQ       │
         │  locality    ← BQ       │
         │  category    ← BQ       │
         │  urgency     ← BQ       │
         │  affectedGroup ← BQ     │
         │  volunteersNeeded ← BQ  │
         │  whyItMatters ← fallback│ ← rich synthetic default
         │  actionGuidance ← fallback                        │
         └──────────┬──────────────┘
                    │
                    ▼
         ┌─────────────────────────┐
         │  Gemini Enrichment      │  ← small, targeted prompt
         │  (Top 4 missions only)  │
         │                         │
         │  Input:  mission IDs    │
         │          + context      │
         │  Output: {              │
         │    "mission_0": {       │
         │      "whyItMatters":"" │  ← max 180 chars
         │      "actionGuidance":""│ ← max 120 chars
         │    }                    │
         │  }                      │
         └──────────┬──────────────┘
                    │
                    ▼ (merge, if enrichment succeeds)
         ┌─────────────────────────┐
         │  Final Payload          │
         │  Structurally complete  │
         │  Narratively enriched   │
         └─────────────────────────┘
```

### Fallback Guarantees

The system is designed so that **Gemini failure is never user-visible**:

| Failure Type | System Behavior |
|---|---|
| `FINISH_REASON: MAX_TOKENS` | Deterministic payload returned, no enrichment. UI renders all fields. |
| `SAFETY` block | Same as above. |
| JSON parse failure | Same. Rich synthetic defaults already populated all cards. |
| API quota exceeded | Catch → fallback. Mission cards never empty. |
| Network timeout | Catch → fallback. |

No page shows a "Connection Interrupted" screen due to an AI failure. The AI makes the product richer — it does not make the product fragile.

---

## Folder Structure

```
Owe/
├── Dockerfile                    # Multi-stage: Node build + Python serve
├── .dockerignore
├── README.md
│
├── backend/
│   ├── main.py                   # FastAPI app, routes, SPA fallback
│   ├── requirements.txt
│   │
│   ├── services/
│   │   ├── ai_service.py         # Hybrid pipeline orchestrator
│   │   ├── bigquery_service.py   # Parallel BQ fetcher + cache
│   │   ├── context_builder.py    # Prompt context assemblers
│   │   ├── gemini_client.py      # Gemini API wrapper + diagnostics
│   │   └── multimodal_service.py # Multimodal extensions (future)
│   │
│   ├── prompts/
│   │   ├── daily_brief_prompt.txt      # Narrative summary enrichment
│   │   ├── mission_generation_prompt.txt# Mission enrichment (why + action)
│   │   ├── civic_chat_prompt.txt        # Conversational AI tone guide
│   │   └── explainability_prompt.txt    # AI reasoning explainability
│   │
│   ├── routes/                   # FastAPI route handlers
│   ├── models/                   # Pydantic models
│   ├── data/                     # Synthetic CSV datasets
│   └── scratch/                  # Dev scripts (not deployed)
│
└── frontend/
    ├── public/
    │   └── logo.svg              # Owe brand mark (used in UI + Chat avatar)
    │
    └── src/
        ├── App.jsx               # Route definitions
        ├── main.jsx
        ├── index.css             # Design system tokens
        │
        ├── pages/
        │   ├── Dashboard.jsx     # Overview + signals + momentum
        │   ├── Missions.jsx      # Community mission cards
        │   └── Chat.jsx          # Civic AI conversational interface
        │
        ├── components/           # Shared UI components
        └── services/
            └── api.js            # Frontend API client
```

---

## BigQuery Dataset Structure

Owe uses a single BigQuery dataset (`owe_civic_data`) with six tables. All tables use UTC timestamps.

### Dataset: `owe_civic_data`

| Table | Description | Key Fields |
|---|---|---|
| `civic_events` | Core civic incident log | `event_id`, `timestamp`, `neighborhood`, `ward`, `category`, `severity`, `resolved` |
| `transport_density` | Road and transit conditions | `neighborhood`, `traffic_density_score`, `avg_vehicle_speed_kmph`, `congestion_level`, `bus_delay_minutes` |
| `environmental_stress` | Environmental risk signals | `neighborhood`, `heat_risk_level`, `flooding_risk`, `aqi`, `timestamp` |
| `accessibility_incidents` | Physical accessibility barriers | `neighborhood`, `issue_type`, `severity`, `response_status`, `timestamp` |
| `community_sentiment` | Neighborhood sentiment signals | `neighborhood`, `sentiment_score`, `dominant_topic`, `frustration_level` |
| `community_missions` | Active and planned civic missions | `mission_title`, `neighborhood`, `category`, `urgency_level`, `affected_group`, `completion_status` |

### Example Schema: `community_missions`

```sql
mission_title     STRING    NOT NULL
neighborhood      STRING    NOT NULL
ward              STRING
category          STRING          -- 'Accessibility', 'Environment', 'Mobility', etc.
urgency_level     STRING          -- 'Low', 'Medium', 'High', 'Critical'
affected_group    STRING          -- 'Seniors', 'Commuters', 'Students', etc.
completion_status STRING          -- 'Active', 'Planned', 'Completed'
created_at        TIMESTAMP NOT NULL
volunteer_count   INTEGER
```

---

## About the Synthetic Dataset

> ⚠️ **Owe currently runs on entirely synthetic data.**

All civic events, transport readings, environmental signals, and mission records are generated programmatically using Python scripts in `backend/data/`. These datasets are designed to be:

- **Statistically realistic** — using probability distributions, temporal patterns, and correlated signals that approximate real urban conditions.
- **Geographically grounded** — using actual Kolkata neighborhoods (Kasba, Jadavpur, Salt Lake, Ballygunge, Gariahat, Behala, Park Circus, Lake Market, Howrah) with realistic lat/lon ranges.
- **Analytics-ready** — clean schemas designed for BigQuery ingestion and SQL aggregation.

Replacing synthetic data with real-time civic feeds (from municipal APIs, crowdsourced reports, or sensor networks) is one of the primary goals of the next development phase.

---

## Local Development Setup

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| Google Cloud SDK | Latest (for BigQuery access) |

### 1. Clone the repository

```bash
git clone https://github.com/your-org/owe.git
cd owe
```

### 2. Configure environment variables

Create a `.env` file in the `backend/` directory:

```env
# Required: Gemini API key from Google AI Studio
GEMINI_API_KEY=your_gemini_api_key_here

# Required for BigQuery: your GCP project ID
GCP_PROJECT_ID=your_gcp_project_id

# Optional: Override default dataset name
BIGQUERY_DATASET=owe_civic_data
```

> If `GEMINI_API_KEY` is absent, the system runs in deterministic fallback mode. All pages render correctly — they simply lack AI-generated narrative enrichment.

> For BigQuery, Application Default Credentials (ADC) are used. Run `gcloud auth application-default login` locally to authenticate.

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies all `/api/*` requests to port `8000` automatically.

---

## Docker & Cloud Run Deployment

Owe builds into a single multi-stage Docker image. The Node build stage compiles the React app into `/dist`. The Python stage copies both the backend and the compiled frontend, then serves everything from a single FastAPI process on port `8080`.

### Local Docker

```bash
# Build
docker build -t owe-mvp .

# Run
docker run -p 8080:8080 \
  -e GEMINI_API_KEY="your_key" \
  -e GCP_PROJECT_ID="your_project" \
  owe-mvp
```

Visit `http://localhost:8080`.

### Google Cloud Run

```bash
gcloud run deploy owe-mvp \
  --source . \
  --port 8080 \
  --region asia-south1 \
  --set-env-vars GEMINI_API_KEY="your_key",GCP_PROJECT_ID="your_project" \
  --allow-unauthenticated
```

Cloud Run handles container scaling, HTTPS termination, and cold-start management automatically. The service scales to zero when not in use.

> **IAM Note**: The Cloud Run service account must have the `BigQuery Data Viewer` and `BigQuery Job User` roles to execute queries against `owe_civic_data`.

---

## AI Prompt Architecture

All prompts are plain text files in `backend/prompts/`. They are loaded at runtime, not embedded in code.

| File | Purpose | Output Shape |
|---|---|---|
| `daily_brief_prompt.txt` | Generates two narrative strings for the dashboard overview | `{ "executive_summary": "...", "momentum_summary": "..." }` |
| `mission_generation_prompt.txt` | Enriches top-N missions with human reasoning | `{ "mission_0": { "whyItMatters": "...", "actionGuidance": "..." }, ... }` |
| `civic_chat_prompt.txt` | Guides the AI's conversational tone and grounding | `{ "reply": "..." }` |
| `explainability_prompt.txt` | Enables the AI to explain its reasoning on demand | Plain text |

**Design principles for all prompts:**

1. **Never ask for structural schema generation.** Prompts only ask for specific text values.
2. **Hard character limits are stated explicitly.** This prevents `MAX_TOKENS` truncation.
3. **Context is pre-assembled by Python, not inferred by the model.** The model enriches; it does not discover.
4. **All prompts end with a valid JSON instruction** to guide output format without relying on `response_mime_type`.

---

## Backend Service Flow

A request to `/api/missions` follows this precise path:

```
1. FastAPI receives GET /api/missions
       │
2.     └── AIService.get_missions()
               │
3.             ├── BigQueryService.fetch_civic_data()      ← parallel fetch (ThreadPoolExecutor)
               │       ├── get_active_missions()           ← LIMIT 15
               │       ├── get_accessibility_incidents()   ← LIMIT 15
               │       ├── get_transport_density()         ← LIMIT 8
               │       └── get_environmental()             ← LIMIT 8
               │         (results cached for 60 seconds)
               │
4.             ├── Deterministic Assembly
               │       For each of 15 missions from BQ:
               │         - map title, locality, category, urgency, affectedGroup
               │         - generate rich synthetic whyItMatters, actionGuidance
               │         - assign volunteersNeeded (deterministic formula)
               │
5.             ├── ContextBuilder.build_missions_context()  ← top 4 missions only
               │
6.             ├── GeminiClient.generate_json_content()
               │       - Load mission_generation_prompt.txt
               │       - Inject context
               │       - max_output_tokens = 1500
               │       - Log finish_reason
               │       - Extract + clean JSON
               │       - Parse enrichment map
               │
7.             ├── Merge enrichments into deterministic cards (top 4)
               │
8.             └── Return final list → HTTP 200 JSON
```

If step 6 fails for any reason, step 8 returns the deterministic payload from step 4 directly. The frontend always receives a structurally complete, render-safe response.

---

## Known Limitations

| Limitation | Notes |
|---|---|
| **Synthetic data only** | All civic signals are generated, not sourced from live municipal feeds. |
| **Kolkata-specific geography** | The neighborhood taxonomy and lat/lon ranges are tailored for Kolkata. Expanding to other cities requires a new dataset. |
| **English only** | No Bengali language support in the AI layer currently. |
| **No user authentication** | The application is currently fully public. User identity, saved missions, and neighborhood preferences are not yet implemented. |
| **No push notifications** | Emerging signals are only surfaced on page load, not via real-time push or background sync. |
| **Gemini quota sensitivity** | High-frequency usage may approach free-tier API limits, causing enrichment to skip and fall back to deterministic responses. |

---

## Roadmap

### Near-term
- [ ] Live municipal data ingestion (Kolkata Municipal Corporation API)
- [ ] Bengali language support in chat interface
- [ ] Mission completion tracking and volunteer coordination
- [ ] Neighborhood-level user accounts (Firebase Auth)

### Medium-term
- [ ] Crowdsourced signal submission from residents
- [ ] Realtime BigQuery streaming for fresh civic events
- [ ] Expanded geography (other Indian metros)
- [ ] Accessibility audit tooling for civic bodies

### Long-term
- [ ] Open API for civic developers to build neighborhood tools on top of Owe's signal infrastructure
- [ ] Integration with mobility and transit platforms (KMRC, WBTC)
- [ ] Formal research partnerships with urban planning institutions

---

## Contributing

Owe is an early-stage civic infrastructure project. Contributions that align with its philosophy — grounded, human-centered, technically rigorous, and free from gamification — are welcome.

**Before contributing:**
1. Read the [Philosophy](#the-philosophy) section carefully. Every design decision in Owe flows from it.
2. Open an issue to discuss your change before submitting a pull request.
3. Ensure your changes do not compromise the [Fallback Guarantees](#fallback-guarantees).

**What we especially welcome:**
- Real civic data integrations
- Accessibility improvements
- Bengali translation
- Prompt quality improvements
- BigQuery query optimizations

---

## License

MIT License. See [LICENSE](./LICENSE) for the full text.

---

<div align="center">

Built with a sense of civic obligation.

*What do we owe each other?*

</div>
