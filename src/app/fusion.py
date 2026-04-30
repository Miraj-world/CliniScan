from __future__ import annotations

from typing import Any

from app.schemas import (
    ConflictResult,
    FusionResult,
    SeverityIndicators,
    SymptomData,
    UrgencyLevel,
    VisionData,
)


SEVERITY_WEIGHTS = {
    "open_wound": 5,
    "bleeding": 5,
    "spreading": 4,
    "discharge": 3,
    "swelling": 2,
    "discoloration": 2,
}

CONFLICT_RISK_BONUS = 2
SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2}


def _dump(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return dict(value or {})


def calculate_vision_score(severity_indicators: SeverityIndicators | dict[str, Any]) -> int:
    indicators = _dump(severity_indicators)
    return sum(
        weight
        for sign, weight in SEVERITY_WEIGHTS.items()
        if bool(indicators.get(sign, False))
    )


def calculate_text_score(symptom_data: SymptomData | dict[str, Any]) -> int:
    data = _dump(symptom_data)
    severity_score = int(data.get("severity_score") or 0)
    base_score = severity_score // 2
    progression_bonus = 2 if data.get("progression") == "worsening" else 0
    risk_factor_bonus = len(data.get("risk_factors") or [])
    return base_score + progression_bonus + risk_factor_bonus


def detect_conflict(
    symptom_data: SymptomData | dict[str, Any],
    vision_data: VisionData | dict[str, Any],
) -> dict[str, Any]:
    symptom = _dump(symptom_data)
    vision = _dump(vision_data)
    text_severity = symptom.get("patient_reported_severity", "low")
    vision_severity = vision.get("visual_severity", "low")

    conflict_map = {
        ("low", "medium"): "minor_discrepancy",
        ("low", "high"): "severity_mismatch",
        ("medium", "high"): "underreporting_possible",
    }
    conflict_type = conflict_map.get((text_severity, vision_severity))

    return ConflictResult(
        conflict_detected=conflict_type is not None,
        conflict_type=conflict_type,
        text_severity=text_severity,
        vision_severity=vision_severity,
    ).model_dump()


def compute_urgency(total_score: int) -> UrgencyLevel:
    if total_score >= 8:
        return "high"
    if total_score >= 4:
        return "medium"
    return "low"


def _build_risk_signals(
    symptom_data: SymptomData | dict[str, Any],
    vision_data: VisionData | dict[str, Any],
    conflict: dict[str, Any],
) -> list[str]:
    symptom = _dump(symptom_data)
    vision = _dump(vision_data)
    indicators = _dump(vision.get("severity_indicators", {}))
    signals: list[str] = []

    if indicators.get("open_wound"):
        signals.append("Open wound detected visually")
    if indicators.get("bleeding"):
        signals.append("Bleeding detected visually")
    if indicators.get("spreading"):
        signals.append("Spreading pattern detected visually")
    if indicators.get("discharge"):
        signals.append("Discharge detected visually")
    if indicators.get("swelling"):
        signals.append("Swelling detected visually")
    if indicators.get("discoloration"):
        signals.append("Discoloration detected visually")
    if symptom.get("progression") == "worsening":
        signals.append("Patient reports worsening progression")
    if symptom.get("risk_factors"):
        signals.append("Patient reported risk factors")
    if conflict.get("conflict_detected"):
        signals.append("Visual evidence suggests higher severity than patient reports")

    return signals


def fuse_evidence(
    symptom_data: SymptomData | dict[str, Any],
    vision_data: VisionData | dict[str, Any],
) -> dict[str, Any]:
    symptom = SymptomData.model_validate(symptom_data)
    vision = VisionData.model_validate(vision_data)

    vision_score = calculate_vision_score(vision.severity_indicators)
    text_score = calculate_text_score(symptom)
    conflict = detect_conflict(symptom, vision)
    total_score = vision_score + text_score

    if conflict["conflict_detected"]:
        total_score += CONFLICT_RISK_BONUS

    result = FusionResult(
        vision_score=vision_score,
        text_score=text_score,
        total_risk_score=total_score,
        urgency=compute_urgency(total_score),
        conflict=ConflictResult.model_validate(conflict),
        risk_signals=_build_risk_signals(symptom, vision, conflict),
    )
    return result.model_dump()
