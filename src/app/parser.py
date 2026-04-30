from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from app.confidence import normalize_diagnosis_confidence
from app.schemas import DiagnosisResult, STANDARD_DISCLAIMER


def fallback_diagnosis() -> dict[str, Any]:
    return {
        "possible_conditions": [],
        "confidence_levels": [],
        "urgency": "medium",
        "red_flags": ["Unable to fully parse AI output"],
        "recommendation": "Please consult a licensed medical professional.",
        "clinical_reasoning": [],
        "disclaimer": STANDARD_DISCLAIMER,
    }


def strip_markdown_fences(response_text: str) -> str:
    text = response_text.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return text
    return text[start : end + 1]


def parse_diagnosis_response(response_text: str) -> dict[str, Any]:
    try:
        cleaned = strip_markdown_fences(response_text)
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            parsed = json.loads(_extract_json_object(strip_markdown_fences(response_text)))
        except json.JSONDecodeError:
            return fallback_diagnosis()

    if not isinstance(parsed, dict):
        return fallback_diagnosis()

    parsed.setdefault("disclaimer", STANDARD_DISCLAIMER)
    parsed["disclaimer"] = parsed.get("disclaimer") or STANDARD_DISCLAIMER
    parsed = normalize_diagnosis_confidence(parsed)

    try:
        return DiagnosisResult.model_validate(parsed).model_dump()
    except ValidationError:
        return fallback_diagnosis()


safe_parse_diagnosis_response = parse_diagnosis_response
