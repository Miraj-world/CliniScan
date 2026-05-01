from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import asyncpg

sys.path.append(str(Path(__file__).resolve().parent.parent))

from db.embeddings import build_case_text, get_embedding

DB_URL = os.getenv("DATABASE_URL_RAW", "postgresql://postgres:postgres@localhost:5432/cliniscan")
SEED_FILE = Path(__file__).parent / "seed_cases.json"


async def seed():
    cases = json.loads(SEED_FILE.read_text())
    conn = await asyncpg.connect(DB_URL)

    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    schema = (Path(__file__).parent / "schema.sql").read_text()
    await conn.execute(schema)

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    inserted = 0

    for case in cases:
        text = build_case_text(case)
        embedding = await get_embedding(text, api_key)
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

        await conn.execute(
            """
            INSERT INTO clinical_cases (
                case_id, body_region, condition_confirmed, urgency_level,
                visual_severity, open_wound, bleeding, swelling, spreading,
                discoloration, discharge, detected_signs, symptom_keywords,
                duration_days_range, severity_score_range, red_flags,
                recommendation, source_dataset, embedding
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19::vector)
            ON CONFLICT (case_id) DO NOTHING
            """,
            case["case_id"],
            case["body_region"],
            case["condition_confirmed"],
            case["urgency_level"],
            case.get("visual_severity"),
            case.get("open_wound", False),
            case.get("bleeding", False),
            case.get("swelling", False),
            case.get("spreading", False),
            case.get("discoloration", False),
            case.get("discharge", False),
            case.get("detected_signs", []),
            case.get("symptom_keywords", []),
            case.get("duration_days_range"),
            case.get("severity_score_range"),
            case.get("red_flags", []),
            case.get("recommendation"),
            "seed",
            embedding_str,
        )
        inserted += 1
        print(f"  ? {case['case_id']} - {case['condition_confirmed']}")

    await conn.close()
    print(f"\nSeeded {inserted} cases successfully.")


if __name__ == "__main__":
    asyncio.run(seed())

