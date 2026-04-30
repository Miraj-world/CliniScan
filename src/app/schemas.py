from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr


UrgencyLevel = Literal["low", "medium", "high"]
ConfidenceLevel = Literal["low", "medium", "high"]
ProgressionLevel = Literal["improving", "stable", "worsening"]
BorderDefinition = Literal["defined", "diffuse", "irregular"]

STANDARD_DISCLAIMER = "Not a diagnosis. Always consult a licensed medical professional."


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class SeverityIndicators(StrictModel):
    open_wound: StrictBool = False
    bleeding: StrictBool = False
    swelling: StrictBool = False
    spreading: StrictBool = False
    discoloration: StrictBool = False
    discharge: StrictBool = False


class SymptomData(StrictModel):
    primary_symptom: StrictStr = ""
    body_location: StrictStr = ""
    duration_days: StrictInt = Field(default=0, ge=0)
    severity_score: StrictInt = Field(default=0, ge=0, le=10)
    progression: ProgressionLevel = "stable"
    associated_symptoms: list[StrictStr] = Field(default_factory=list)
    patient_reported_severity: UrgencyLevel = "low"
    risk_factors: list[StrictStr] = Field(default_factory=list)


class VisionData(StrictModel):
    visual_features: dict[StrictStr, StrictStr] = Field(default_factory=dict)
    detected_signs: list[StrictStr] = Field(default_factory=list)
    severity_indicators: SeverityIndicators = Field(default_factory=SeverityIndicators)
    visual_severity: UrgencyLevel = "low"
    confidence: ConfidenceLevel = "medium"


class ConflictResult(StrictModel):
    conflict_detected: StrictBool = False
    conflict_type: StrictStr | None = None
    text_severity: UrgencyLevel = "low"
    vision_severity: UrgencyLevel = "low"


class FusionResult(StrictModel):
    vision_score: StrictInt = Field(default=0, ge=0)
    text_score: StrictInt = Field(default=0, ge=0)
    total_risk_score: StrictInt = Field(default=0, ge=0)
    urgency: UrgencyLevel = "low"
    conflict: ConflictResult = Field(default_factory=ConflictResult)
    risk_signals: list[StrictStr] = Field(default_factory=list)


class DiagnosisResult(StrictModel):
    possible_conditions: list[StrictStr] = Field(default_factory=list)
    confidence_levels: list[ConfidenceLevel] = Field(default_factory=list)
    urgency: UrgencyLevel = "medium"
    red_flags: list[StrictStr] = Field(default_factory=list)
    recommendation: StrictStr = "Please consult a licensed medical professional."
    clinical_reasoning: list[StrictStr] = Field(default_factory=list)
    disclaimer: StrictStr = STANDARD_DISCLAIMER
