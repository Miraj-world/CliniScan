# CliniScan

CliniScan is a layered multimodal triage workflow for symptom intake and risk assessment. It combines patient-reported symptoms, optional image input, body location, duration, severity, age, medications, and known conditions to return a structured triage summary.

The product is designed for hackathon demo use as a clinical decision-support prototype. It is not a medical device and it does not diagnose users.

## Safety Disclaimer

Every user-facing result must preserve this message:

> Not a medical diagnosis. Always consult a licensed medical professional.

CliniScan should describe results as possible conditions, risk signals, red flags, urgency level, clinical assessment, and recommended next step. Avoid language that implies a confirmed diagnosis.

## Current Capabilities

- Structured symptom intake with body location, duration, severity, age, known conditions, and medications.
- Optional image upload for visual evidence extraction.
- Frontend live analysis sends requests through OpenAI using `gpt-5.5`.
- Deterministic evidence fusion that combines text and visual signals into a risk score.
- Conflict detection when patient-reported severity and image-based severity disagree.
- Safety override and red flag detection for urgent symptoms.
- Quality gate for uncertain or limited inputs.
- JSON-only clinical reasoning layer with safe fallback behavior.
- Polished React/Vite frontend with centered transparent logo header, step indicator, custom severity slider, animated upload dropzone, processing animation, and results dashboard views.

## Architecture

```text
CliniScan/
  backend/
    main.py                    FastAPI app with /health and /analyze
    check_api_keys.py          Local API key smoke test
    cache/                     Demo scenario responses
    layers/
      ai_gateway.py            Anthropic/OpenAI API adapters
      safety_override.py       Deterministic urgent keyword checks
      vision_extractor.py      Image-to-structured-vision layer
      symptom_structurer.py    Text-to-structured-symptom layer
      evidence_fusion.py       Deterministic risk scoring and mismatch detection
      quality_gate.py          Input quality scoring
      clinical_reasoning.py    Final structured reasoning prompt
      json_parser.py           JSON parsing, normalization, and fallback handling
    models/
      schemas.py               Pydantic request/response contracts
  frontend/
    src/
      App.jsx                  App shell and API orchestration
      components/              Intake, progress, result, alert, and badge components
      assets/                  Frontend image assets, including the transparent logo
      index.css                UI design system and responsive styling
```

## Backend Pipeline

1. Safety override scans symptom text for urgent keywords.
2. Symptom structurer converts text fields into a structured symptom object.
3. Vision extractor converts an uploaded image into structured visual evidence when an image is provided.
4. Evidence fusion computes text score, vision score, total risk score, urgency, risk signals, and conflict status.
5. Quality gate evaluates whether the input is strong enough for confident triage support.
6. Clinical reasoning receives only structured evidence and returns possible conditions, confidence levels, assessment text, red flags, recommendation, and disclaimer.
7. JSON parser validates and normalizes model output; invalid model output falls back safely.

## AI Providers And Models

The API keys only authenticate with each provider. The model names are selected in code:

- Anthropic: `claude-sonnet-4-6`
- OpenAI: `gpt-5.5`

Current model constants live in `backend/layers/ai_gateway.py`.

The current frontend does not expose a provider selector. It sends `provider: "openai"` in the `/analyze` payload, so normal app usage requires `OPENAI_API_KEY` in `backend/.env`.

The backend still supports Anthropic for API-level use and local testing if `ANTHROPIC_API_KEY` is configured.

## API Endpoints

### `GET /health`

Returns backend status, provider configuration status, and selected model names.

### `POST /analyze`

Required JSON fields:

- `symptom_text`
- `body_location`
- `duration_days`
- `severity_score`
- `provider`

Optional fields:

- `age`
- `known_conditions`
- `medications`
- `image_base64`
- `image_mime`
- `demo_scenario`

`provider` must be either `anthropic` or `openai`.

`demo_scenario` can be `1`, `2`, or `3`.

Note: the current frontend submits live assessments with `provider: "openai"` and does not display provider or demo controls.

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key for current frontend usage
- Optional Anthropic API key for API-level testing

### 1. Backend Environment

From the repo root:

```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key_optional
```

Install backend dependencies:

```bash
cd backend
python3 -m venv ../.venv
../.venv/bin/python -m pip install -r requirements.txt
```

Optional API key smoke test:

```bash
cd backend
../.venv/bin/python check_api_keys.py
```

Start the backend:

```bash
cd backend
../.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Backend URL:

```text
http://127.0.0.1:8001
```

### 2. Frontend Environment

In a separate terminal, from the repo root:

```bash
cd frontend
npm install
VITE_API_URL=http://127.0.0.1:8001 npm run dev -- --host 127.0.0.1 --port 3002
```

Frontend URL:

```text
http://127.0.0.1:3002
```

Alternative default ports also work if they are free. Start the backend on `8000`, then run the frontend on its default Vite port:

```bash
cd backend
../.venv/bin/python -m uvicorn main:app --reload --port 8000

cd ../frontend
npm run dev
```

## Demo Scenarios

The backend still includes three cached demo scenarios:

- Skin Rash
- Minor Burn
- Eye Redness

Demo scenarios call the backend with `demo_scenario` and return cached responses from `backend/cache/`. They are useful for API testing and presentation fallback because they do not require live model calls. The current frontend does not show demo scenario buttons.

## Verification

Run backend tests from the repo root:

```bash
.venv/bin/python -m pytest
```

Run the frontend production build:

```bash
cd frontend
npm run build
```

Expected current verification:

```text
19 backend tests passing
frontend Vite build passing
```

## Known Limitations

- CliniScan is a hackathon prototype, not a clinically validated medical device.
- It does not store user history or provide authentication.
- Uploaded images are sent as base64 request payloads to the backend.
- Live analysis requires configured provider API keys.
- Model output is constrained and validated, but the system still requires clinician review.

## Team Workflow

Recommended debugging flow:

```bash
git checkout main
git pull origin main
```

Create a branch for new work:

```bash
git checkout -b your-branch-name
```

Before pushing:

```bash
.venv/bin/python -m pytest
cd frontend
npm run build
```
