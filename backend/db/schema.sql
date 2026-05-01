CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS clinical_cases (
  id SERIAL PRIMARY KEY,
  case_id TEXT UNIQUE NOT NULL,
  body_region TEXT NOT NULL,
  condition_confirmed TEXT NOT NULL,
  urgency_level TEXT NOT NULL CHECK (urgency_level IN ('low', 'medium', 'high')),
  visual_severity TEXT,
  open_wound BOOLEAN DEFAULT FALSE,
  bleeding BOOLEAN DEFAULT FALSE,
  swelling BOOLEAN DEFAULT FALSE,
  spreading BOOLEAN DEFAULT FALSE,
  discoloration BOOLEAN DEFAULT FALSE,
  discharge BOOLEAN DEFAULT FALSE,
  detected_signs TEXT[],
  symptom_keywords TEXT[],
  duration_days_range TEXT,
  severity_score_range TEXT,
  red_flags TEXT[],
  recommendation TEXT,
  source_dataset TEXT DEFAULT 'seed',
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS clinical_cases_embedding_idx
  ON clinical_cases USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 10);
