from __future__ import annotations

import httpx

ANTHROPIC_EMBED_URL = "https://api.anthropic.com/v1/messages"


def build_case_text(case: dict) -> str:
    return (
        f"Body region: {case.get('body_region', '')}. "
        f"Symptoms: {', '.join(case.get('symptom_keywords', []))}. "
        f"Visual signs: {', '.join(case.get('detected_signs', []))}. "
        f"Duration: {case.get('duration_days_range', '')} days. "
        f"Severity score range: {case.get('severity_score_range', '')}. "
        f"Condition: {case.get('condition_confirmed', '')}. "
        f"Urgency: {case.get('urgency_level', '')}."
    )


def build_query_text(fusion_output: dict, symptom_output: dict) -> str:
    signs = fusion_output.get("risk_signals", [])
    region = fusion_output.get("body_region", "")
    urgency = fusion_output.get("urgency", "")
    symptom = symptom_output.get("primary_symptom", "")
    keywords = symptom_output.get("associated_symptoms", [])
    duration = symptom_output.get("duration_days", "")
    severity = symptom_output.get("severity_score", "")
    return (
        f"Body region: {region}. "
        f"Primary symptom: {symptom}. "
        f"Associated symptoms: {', '.join(keywords)}. "
        f"Risk signals: {', '.join(signs)}. "
        f"Duration: {duration} days. "
        f"Severity score: {severity}. "
        f"Estimated urgency: {urgency}."
    )


async def get_embedding(text: str, api_key: str) -> list[float]:
    """Use Claude via a trick: embed by asking for a fixed-length feature vector.
    For production use OpenAI text-embedding-3-small or a dedicated embed endpoint.
    Here we use OpenAI embeddings if OPENAI_API_KEY is set, else fall back to random seeded vector for dev.
    """
    import hashlib
    import os
    import random
    import struct

    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if openai_key:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                json={"model": "text-embedding-3-small", "input": text},
            )
            resp.raise_for_status()
            return resp.json()["data"][0]["embedding"]
    else:
        # Dev fallback: deterministic pseudo-embedding from text hash (1536-dim)
        h = hashlib.sha256(text.encode()).digest()
        seed = struct.unpack("I", h[:4])[0]
        rng = random.Random(seed)
        vec = [rng.gauss(0, 1) for _ in range(1536)]
        mag = sum(x**2 for x in vec) ** 0.5
        return [x / mag for x in vec]
