# Owe — AI-Powered Civic Reciprocity Platform

Owe is a humane, calm, and thoughtful civic coordination application. Inspired by T. M. Scanlon's moral philosophy, Owe helps neighbors recognize their shared obligations and coordinate small, meaningful acts of mutual support based on fragmented civic signals.

---

## 1. The Problem
Modern smart city dashboards treat urban spaces as spreadsheets, optimizing transit metrics and logging complaints while ignoring the human element. Conversely, social networks foster noise and outrage, turning local concerns into platforms for grievance rather than action. Vulnerable residents (seniors, students, disabled individuals) are often left isolated by temporary physical barriers or infrastructure failures because there is no channel translating civic friction into community solidarity.

## 2. The Philosophy
> *"To justify one's actions to others is a basic human need."*  
> — T. M. Scanlon, **What We Owe to Each Other**

Owe operates on the principle of **civic reciprocity**. We reject gamification, points, and dashboards of outrage. Instead, Owe focuses on mutual obligation—identifying where access or wellbeing has compromised, explaining *why* support is needed, and framing actions as simple duties of care that neighbors owe to one another sharing a common locality.

## 3. The Solution
Owe aggregates fragmented data signals (like accessibility incidents, waterlogging complaints, air quality drops, and transit disruptions) and synthesizes them into:
1. **Daily Community Brief**: An overview of collective neighborhood wellness and emerging friction.
2. **Community Momentum**: A record of resolutions, successful neighbor interventions, and recovery milestones that fosters hope and participation.
3. **Humane Community Missions**: Non-transactional, localized invitations to support specific resident groups.
4. **Conversational Civic Intelligence**: A calm AI assistant that explains the logic behind its observations using concrete data markers.

---

## 4. Features
* **Emerging Civic Signals**: Highly contextual, explaining the overlap of multiple data points (e.g. how a drainage clog near Kasba Post Office isolates seniors and disrupts bypass traffic).
* **Community Momentum Tracker**: Visually highlights resolved issues (e.g. tactile pathways cleared by volunteers in Behala) to showcase collective progress.
* **Story-Driven Mission Cards**: Structured to explain *Why It Matters*, removing corporate volunteer speak or gamified mechanics.
* **Grounded Geography**: Focuses on Kolkata-specific localities (Kasba, Jadavpur, Salt Lake, Ballygunge, Gariahat, Behala) for hyper-local relevance.

---

## 5. Architecture

### System Architecture Diagram
```
              [ Client / Browser ] (React Single Page App)
                       │
                       │ HTTP / JSON
                       ▼
            [ FastAPI Web Server ] (Port 8080)
             ├── /api/health
             ├── /api/brief
             ├── /api/missions
             └── /api/chat
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       [ AIService ]      [ Static File Router ]
       (Prompt / Fallback) (Mounts /dist on root "/")
             │
      ┌──────┴──────┐
      ▼             ▼
[Gemini Client] [Civic Feeds JSON]
```

### Frontend-Backend Communication
* **Vite Proxy (Local Development)**: Frontend code is executed via Vite on `localhost:5173`. All backend API calls matching `/api/*` are dynamically proxied to `localhost:8000`.
* **FastAPI SPA Fallback (Production)**: The frontend assets are compiled into `/frontend/dist`. FastAPI serves static assets under `/assets/` and utilizes a catch-all route redirecting root and route paths (like `/missions`, `/chat`) back to `index.html`. This supports client-side SPA routing natively, resolving direct refreshes.

---

## 6. AI Layer & Gemini Integration

### Prompt Architecture
The AI Service uses structured prompt templates loaded from `backend/prompts/`:
* `daily_brief_prompt.txt`: Synthesizes feeds, scores pulse, and assigns signal strengths.
* `mission_generation_prompt.txt`: Outlines how to generate collaborative local tasks.
* `civic_chat_prompt.txt`: Enforces the observant, humane, and restrained tone.

### Failsafe Fallback Engine
When the `GEMINI_API_KEY` is not present, or if a quota limit or timeout is hit during execution, Owe automatically routes requests to a local rule-based simulation engine in `ai_service.py`. This ensures:
1. The app remains fully functional and "alive" during pitch demos.
2. The UI continues to serve authentic, synthesized insights and responses based on the active JSON data feeds.

---

## 7. Setup & Run Instructions

### Option A: Local Dev Setup (Requires Python 3.11+ & Node 18+)

1. **Backend Server**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
2. **Frontend client**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

---

## 8. Docker & Cloud Run Deployment

Owe builds into a single multi-stage Docker container where the backend serves both API endpoints and frontend assets on port `8080`.

### Local Docker execution
1. Build the container:
   ```bash
   docker build -t owe-mvp .
   ```
2. Run the container:
   ```bash
   docker run -p 8080:8080 -e GEMINI_API_KEY="your-api-key" owe-mvp
   ```
3. Verify via `http://localhost:8080`.

### Google Cloud Run Deployment
Deploy the container with a single command:
```bash
gcloud run deploy owe-mvp \
  --source . \
  --port 8080 \
  --set-env-vars GEMINI_API_KEY="your-api-key" \
  --allow-unauthenticated
```
This builds your container in the cloud via Google Cloud Build and hosts it instantly on a scalable serverless platform.
