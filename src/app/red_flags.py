from __future__ import annotations

from typing import Any

from app.schemas import FusionResult, SymptomData


def _dump(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return dict(value or {})


def _combined_text(symptom_data: dict[str, Any], fusion_result: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("primary_symptom", "body_location"):
        parts.append(str(symptom_data.get(key, "")))
    parts.extend(str(item) for item in symptom_data.get("associated_symptoms") or [])
    parts.extend(str(item) for item in symptom_data.get("risk_factors") or [])
    parts.extend(str(item) for item in fusion_result.get("risk_signals") or [])
    return " ".join(parts).lower()


def detect_red_flags(
    symptom_data: SymptomData | dict[str, Any],
    fusion_result: FusionResult | dict[str, Any] | None = None,
) -> list[str]:
    symptom = _dump(symptom_data)
    fusion = _dump(fusion_result)
    text = _combined_text(symptom, fusion)
    severity_score = int(symptom.get("severity_score") or 0)
    flags: list[str] = []

    if severity_score >= 8 or any(
        phrase in text for phrase in ("severe pain", "extreme pain", "unbearable pain")
    ):
        flags.append("Severe pain reported")

    if any(
        phrase in text
        for phrase in ("rapid spreading", "spreading pattern", "spreading quickly")
    ):
        flags.append("Rapid spreading reported or detected")

    if "fever" in text and "rash" in text:
        flags.append("Fever with rash reported")

    if (
        "eye" in text
        and any(phrase in text for phrase in ("pain", "light sensitivity", "photophobia"))
    ):
        flags.append("Eye pain or light sensitivity reported")

    if "discharge" in text:
        flags.append("Discharge reported or detected")

    if any(
        phrase in text
        for phrase in (
            "uncontrolled bleeding",
            "bleeding will not stop",
            "bleeding won't stop",
            "cannot stop bleeding",
        )
    ):
        flags.append("Uncontrolled bleeding reported")

    if any(
        phrase in text
        for phrase in (
            "infection",
            "pus",
            "red streak",
            "warm to touch",
            "increasing redness",
        )
    ):
        flags.append("Signs of infection reported")

    return flags
