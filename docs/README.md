# CliniScan Documentation

This folder is for supporting project documentation. The main setup and run instructions live in the root `README.md`.

## Product Summary

CliniScan is a multimodal triage-support prototype. It accepts symptom text, structured context fields, and an optional image, then returns a structured risk assessment with possible conditions, confidence levels, risk signals, red flags, urgency, clinical assessment, and recommended next step.

CliniScan is not a diagnosis tool. It should always direct users to licensed medical professionals.

## Current Backend Modules

- `backend/models/schemas.py`: Pydantic request and response contracts.
- `backend/layers/safety_override.py`: Deterministic urgent keyword detection.
- `backend/layers/symptom_structurer.py`: LLM prompt layer for symptom text structuring.
- `backend/layers/vision_extractor.py`: LLM prompt layer for image feature extraction.
- `backend/layers/evidence_fusion.py`: Deterministic multimodal risk scoring.
- `backend/layers/quality_gate.py`: Input quality and uncertainty scoring.
- `backend/layers/clinical_reasoning.py`: JSON-only clinical reasoning prompt.
- `backend/layers/json_parser.py`: JSON parsing, schema normalization, and fallback output.
- `backend/layers/ai_gateway.py`: Anthropic and OpenAI request adapters.
- `backend/main.py`: FastAPI app and pipeline orchestration.

## Current Frontend

- React + Vite single-page app.
- Three main views: symptom intake, processing progress, and results dashboard.
- Live frontend analysis currently sends `provider: "anthropic"`.
- The current UI does not expose provider selection or demo scenario buttons.
- The header uses a transparent CliniScan logo asset from `frontend/src/assets/CliniScanLogo.png`.
- Styled with `frontend/src/index.css`.
- Icons are provided by `lucide-react`.

## Validation

From the repo root:

```bash
.venv/bin/python -m pytest
```

From `frontend/`:

```bash
npm run build
```
