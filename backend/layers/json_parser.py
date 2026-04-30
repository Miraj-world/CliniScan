from __future__ import annotations

import json
import re
from typing import Any

from models.schemas import STANDARD_DISCLAIMER


def extract_json_object(text: str) -> str:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        return cleaned
    return cleaned[start : end + 1]


def parse_json_object(text: str, fallback: dict[str, Any]) -> dict[str, Any]:
    raw = extract_json_object(text)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return dict(fallback)
    if not isinstance(value, dict):
        return dict(fallback)
    return value


def normalize_confidence_level(value: Any) -> str:
    if isinstance(value, (float, int)):
        if value > 1:
            value = value / 100
        if value >= 0.67:
            return "High"
        if value <= 0.33:
            return "Low"
        return "Medium"

    text = str(value or "").strip().lower()
    if re.search(r"\bhigh|strong|likely|probable\b", text):
        return "High"
    if re.search(r"\blow|unlikely|weak|doubtful\b", text):
        return "Low"
    return "Medium"


def normalize_diagnosis_output(data: dict[str, Any]) -> dict[str, Any]:
    out = dict(data)
    conditions = out.get("possible_conditions") or []
    if not isinstance(conditions, list):
        conditions = []
    out["possible_conditions"] = [str(item) for item in conditions if str(item).strip()]

    levels = out.get("confidence_levels") or []
    if not isinstance(levels, list):
        levels = []
    normalized_levels = [normalize_confidence_level(item) for item in levels]
    normalized_levels = normalized_levels[: len(out["possible_conditions"])]
    while len(normalized_levels) < len(out["possible_conditions"]):
        normalized_levels.append("Medium")
    out["confidence_levels"] = normalized_levels

    reasoning = out.get("clinical_reasoning") or []
    if not isinstance(reasoning, list):
        reasoning = []
    out["clinical_reasoning"] = [str(item) for item in reasoning if str(item).strip()][:3]

    red_flags = out.get("red_flags") or []
    if not isinstance(red_flags, list):
        red_flags = []
    out["red_flags"] = [str(item) for item in red_flags if str(item).strip()]

    out["recommendation"] = str(out.get("recommendation") or "Seek medical evaluation if symptoms persist or worsen.")
    out["disclaimer"] = STANDARD_DISCLAIMER
    return out


def fallback_diagnosis() -> dict[str, Any]:
    return {
        "possible_conditions": [],
        "confidence_levels": [],
        "clinical_reasoning": [
            "Insufficient structured evidence was available to produce a reliable triage summary.",
            "The current result is conservative and should not be used as a diagnosis.",
            "A licensed clinician should review symptoms directly.",
        ],
        "red_flags": ["Clinical reasoning output could not be parsed reliably"],
        "recommendation": "Seek medical evaluation if symptoms persist or worsen.",
        "disclaimer": STANDARD_DISCLAIMER,
    }
