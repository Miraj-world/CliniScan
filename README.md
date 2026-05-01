# CliniScan

CliniScan is a layered multimodal triage support app for hackathon/demo use. It combines symptom text, structured intake fields, and optional image analysis to generate urgency guidance and a structured report.

## Safety

CliniScan is **not** a diagnosis tool and not a replacement for licensed care.

> Not a medical diagnosis. Always consult a licensed medical professional.

## Current Features

- Structured intake: symptom text, body location, duration, pain severity (1-10), age, known conditions, medications.
- Optional image upload (`jpg/png/webp`) for visual evidence extraction.
- Layered backend pipeline:
  - safety override
  - symptom structuring
  - vision extraction
  - deterministic evidence fusion
  - pgvector RAG retrieval (similar-case grounding)
  - quality gate
  - clinical reasoning
- Results dashboard with:
  - urgency badge
  - possible conditions + confidence
  - clinical assessment
  - risk signals and red flags
  - submitted-input toggle (shows uploaded image + entered fields)
- Report actions (top-right in Reports view):
  - Download PDF
  - Share (native share sheet, clipboard fallback)

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI
- AI providers: OpenAI + Anthropic (provider selected in backend request; current frontend sends `openai`)

## Repository Layout

```text
CliniScan/
  backend/
    main.py
    requirements.txt
    .env.example
    cache/
    db/
    layers/
    models/
  frontend/
    package.json
    src/
  tests/
  README.md
  requirements.txt
```

## Setup

### 1) Backend

```bash
cd backend
python -m venv ..\.venv
..\.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```

Set API keys in `backend/.env`:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/cliniscan
DATABASE_URL_RAW=postgresql://postgres:postgres@localhost:5432/cliniscan
```

### 1b) pgvector RAG database setup

```bash
# 1. Create the database
createdb cliniscan

# 2. Install pgvector extension (if not already)
psql cliniscan -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 3. Run seed script
python db/seed.py

# 4. Start the server normally
uvicorn main:app --reload
```

Run backend:

```bash
cd backend
..\.venv\Scripts\python -m uvicorn main:app --reload --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Default URLs:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

If needed, override frontend API URL:

```bash
set VITE_API_URL=http://localhost:8000
npm run dev
```

## API

### `GET /health`
Returns backend/provider status.

### `POST /analyze`
JSON body:

- Required: `symptom_text`, `body_location`, `duration_days`, `severity_score`, `provider`
- Optional: `age`, `known_conditions`, `medications`, `image_base64`, `image_mime`, `demo_scenario`

## Verification

Run tests:

```bash
python -m pytest -q
```

Build frontend:

```bash
cd frontend
npm run build
```

Current baseline: backend tests passing and frontend production build passing.
