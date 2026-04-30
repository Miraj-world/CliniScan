# CliniScan v2

CliniScan is a rule-augmented multimodal triage assistant that fuses structured symptom intake and visual evidence.

## What It Is
- A layered triage prioritization workflow with deterministic risk fusion.
- Explainable pipeline output for demo and educational use.

## What It Is Not
- Not a diagnosis tool.
- Not a replacement for licensed medical consultation.
- Not a clinically validated medical device.

Every result includes: `Not a diagnosis. Always consult a licensed medical professional.`

## Architecture
- `backend/`
  - FastAPI orchestration (`/analyze`, `/health`)
  - Layered modules:
    - Layer 0: Safety override
    - Layer 1A: Vision extractor (LLM)
    - Layer 1B: Symptom structurer (LLM)
    - Layer 2: Evidence fusion (deterministic)
    - Layer 3: Quality gate (deterministic)
    - Layer 4: Clinical reasoning (LLM)
  - Demo cache scenarios in `backend/cache/`
- `frontend/`
  - React + Vite SPA with 3-view state machine:
    - Input
    - Processing pipeline
    - Results

## API Contract
`POST /analyze` expects JSON:
- `symptom_text`, `body_location`, `duration_days`, `severity_score`
- optional: `age`, `known_conditions`, `medications`
- optional image: `image_base64`, `image_mime`
- optional demo: `demo_scenario` (`1|2|3`)
- `provider`: `anthropic` or `openai`

Returns:
- `pipeline_stages`, `diagnosis`, `urgency`, `conflict`, `risk_signals`, `quality`, `no_image_mode`, `demo_mode`

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- API keys: Create a `.env` file in `backend/` with:
  ```
  ANTHROPIC_API_KEY=your_anthropic_key
  OPENAI_API_KEY=your_openai_key
  ```

### Backend
```bash
# From the CliniScan root directory
cd backend
pip install -r requirements.txt
copy .env.example .env    # Then edit .env with your API keys
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
# From the CliniScan root directory (separate terminal)
cd frontend
npm install
npm run dev
```

### Running the Application

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   python -m uvicorn main:app --reload --port 8000
   ```
   Backend runs at: `http://localhost:8000`

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend typically runs at: `http://localhost:3000` (or next available port)

3. Open the frontend URL in your browser
