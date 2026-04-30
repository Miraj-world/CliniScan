# CliniScan Documentation

## Project Overview

CliniScan is a multimodal symptom triage prototype. It is designed to take patient-reported symptom text and, when available, an uploaded image. The backend converts those inputs into structured data, fuses evidence with deterministic scoring, and returns an urgency-oriented result for a hackathon demo.

This project is not intended to diagnose medical conditions. It is a decision-support prototype that should consistently direct users to licensed medical professionals.

## Pipeline

1. Patient enters symptom text, body location, duration, severity, and optional background context.
2. Patient optionally uploads an image.
3. The backend asks the selected LLM to structure the symptom text into the `SymptomData` schema.
4. If an image is provided, the backend asks the selected LLM to return visual observations in the `VisionData` schema.
5. `fuse_evidence()` computes text score, vision score, conflict status, risk signals, and urgency.
6. `detect_red_flags()` adds deterministic safety flags.
7. The diagnosis prompt receives only structured fusion output and returns JSON that validates against `DiagnosisResult`.
8. The parser normalizes confidence values and falls back safely if model output is invalid.

## Implemented Modules

- `src/app/schemas.py`: Pydantic data contracts.
- `src/app/fusion.py`: Deterministic multimodal urgency scoring.
- `src/app/parser.py`: Safe JSON parsing and fallback response handling.
- `src/app/confidence.py`: Confidence normalization.
- `src/app/red_flags.py`: Deterministic red flag detection.
- `src/app/prompts.py`: JSON-only prompt templates.
- `src/app/main.py`: FastAPI entry point and LLM provider wiring.
- `src/index.html`: Browser-based React prototype.

## Demo Modes

Demo mode runs entirely in the browser using mock data. It is useful for presenting the product flow when API keys or network calls are unavailable.

Live mode calls the FastAPI backend. The user can choose Anthropic or OpenAI and provide a matching API key in the frontend sidebar.

## Known Limitations

- Live LLM calls require user-provided API keys.
- There is no persistent storage.
- There is no authentication.
- Uploaded images are sent as base64 request payloads.
- The current frontend is a single static HTML prototype.
- The system is for triage support only, not diagnosis.

## Validation

Run the backend tests with:

```bash
PYTHONPATH=src python -m pytest
```

The test suite covers the deterministic logic modules and API smoke behavior without calling external AI providers.
