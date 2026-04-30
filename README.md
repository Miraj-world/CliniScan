# CliniScan

CliniScan is a hackathon prototype for AI-assisted symptom triage. It combines structured patient symptom text with optional image evidence, produces a deterministic urgency signal, and then asks an LLM for JSON-only clinical reasoning that is clearly marked as not a diagnosis.

- Team: The Big O(1)
- Hackathon: HCBC Hackathon 2026
- Theme: AI for a Smarter Tomorrow

## Current Status

- Backend fusion logic is implemented and tested.
- FastAPI exposes `/health` and `/analyze`.
- The frontend is a single-file React prototype at `src/index.html`.
- Demo mode works without API keys.
- Live mode supports Anthropic and OpenAI through user-provided API keys.
- The project has pytest coverage for fusion, parsing, confidence cleanup, red flags, and API smoke behavior.

## Repository Layout

```text
demo/                 Demo screenshots or video assets
docs/                 Project documentation
src/app/              FastAPI backend and triage logic
src/index.html        React frontend prototype
tests/                Pytest test suite
requirements.txt      Python dependencies
START_HACKATHON.md    Required hackathon verification file
```

## Backend Setup

Use Python 3.12 for the most reliable install path.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If your default `python3` is already Python 3.12, using `python3 -m venv .venv` is fine.

## Run The Backend

```bash
source .venv/bin/activate
PYTHONPATH=src python -m uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "models": {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o"
  }
}
```

## Run The Frontend

Open `src/index.html` in a browser.

The UI starts in demo mode, which does not call the backend. For live mode:

1. Start the backend.
2. Toggle live mode in the sidebar.
3. Choose Anthropic or OpenAI.
4. Enter the matching API key.
5. Keep the backend URL as `http://localhost:8000` unless you started it elsewhere.

## Run Tests

```bash
source .venv/bin/activate
python -m pytest
```

Current expected result:

```text
20 passed
```

## API Summary

`GET /health`

Returns backend status and configured model names.

`POST /analyze`

Accepts structured symptom inputs, optional base64 image data, a provider, and an API key. The backend runs:

1. Optional image feature extraction through the selected LLM.
2. Symptom text structuring through the selected LLM.
3. Deterministic evidence fusion and urgency scoring.
4. Red flag detection.
5. JSON-only diagnosis-style reasoning through the selected LLM.

The response includes `fusion`, `diagnosis`, `has_image`, and `provider`.

## Medical Safety Note

CliniScan is not a diagnostic system. It is a prototype for structured triage support, and every generated result must include:

```text
Not a diagnosis. Always consult a licensed medical professional.
```
