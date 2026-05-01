from __future__ import annotations

import os

from db.embeddings import build_query_text, get_embedding

DB_URL = os.getenv("DATABASE_URL_RAW", "postgresql://postgres:postgres@localhost:5432/cliniscan")
TOP_K = 3
MIN_SIMILARITY = 0.72


async def retrieve_similar_cases(
    fusion_output: dict,
    symptom_output: dict,
    api_key: str,
) -> list[dict]:
    import asyncpg

    try:
        query_text = build_query_text(fusion_output, symptom_output)
        query_embedding = await get_embedding(query_text, api_key)
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        conn = await asyncpg.connect(DB_URL)
        rows = await conn.fetch(
            """
            SELECT
                condition_confirmed,
                urgency_level,
                visual_severity,
                detected_signs,
                symptom_keywords,
                red_flags,
                recommendation,
                body_region,
                1 - (embedding <=> $1::vector) AS similarity
            FROM clinical_cases
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            embedding_str,
            TOP_K,
        )
        await conn.close()

        results = []
        for row in rows:
            if row["similarity"] >= MIN_SIMILARITY:
                results.append(
                    {
                        "condition": row["condition_confirmed"],
                        "urgency": row["urgency_level"],
                        "visual_severity": row["visual_severity"],
                        "detected_signs": list(row["detected_signs"] or []),
                        "symptom_keywords": list(row["symptom_keywords"] or []),
                        "red_flags": list(row["red_flags"] or []),
                        "recommendation": row["recommendation"],
                        "body_region": row["body_region"],
                        "similarity": round(float(row["similarity"]), 3),
                    }
                )
        return results

    except Exception as e:
        print(f"[RAG Retriever] Failed: {e}")
        return []


def format_rag_context(cases: list[dict]) -> str:
    if not cases:
        return ""
    lines = ["RETRIEVED SIMILAR CLINICAL CASES (use as grounding evidence):"]
    for i, c in enumerate(cases, 1):
        lines.append(
            f"\nCase {i} (similarity: {c['similarity']}):"
            f"\n  Condition: {c['condition']}"
            f"\n  Urgency: {c['urgency']}"
            f"\n  Key signs: {', '.join(c['detected_signs'])}"
            f"\n  Red flags: {', '.join(c['red_flags']) if c['red_flags'] else 'none'}"
            f"\n  Recommendation: {c['recommendation']}"
        )
    lines.append("\nUse the above cases to ground your reasoning. Do not copy them verbatim - reason from the evidence.")
    return "\n".join(lines)

