from __future__ import annotations

from typing import Any

from app.schemas import ConfidenceLevel


def normalize_confidence(value: Any) -> ConfidenceLevel:
    if isinstance(value, (int, float)):
        if value > 1:
            value = value / 100
        if value >= 0.67:
            return "high"
        if value <= 0.33:
            return "low"
        return "medium"

    text = str(value).strip().lower()
    if not text:
        return "medium"

    if any(term in text for term in ("low", "weak", "unlikely", "doubtful")):
        return "low"
    if any(term in text for term in ("high", "strong", "likely", "probable")):
        return "high"
    return "medium"


def normalize_confidence_levels(
    confidence_levels: list[Any] | None,
    condition_count: int,
) -> list[ConfidenceLevel]:
    normalized = [normalize_confidence(value) for value in confidence_levels or []]

    if len(normalized) > condition_count:
        return normalized[:condition_count]

    while len(normalized) < condition_count:
        normalized.append("medium")

    return normalized


def normalize_diagnosis_confidence(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    condition_count = len(normalized.get("possible_conditions") or [])
    normalized["confidence_levels"] = normalize_confidence_levels(
        normalized.get("confidence_levels"),
        condition_count,
    )
    return normalized
