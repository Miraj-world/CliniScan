from app.fusion import calculate_text_score, fuse_evidence
from app.schemas import SeverityIndicators, SymptomData, VisionData


def test_low_urgency_case():
    result = fuse_evidence(
        SymptomData(severity_score=2, patient_reported_severity="low"),
        VisionData(visual_severity="low"),
    )

    assert result["urgency"] == "low"
    assert result["total_risk_score"] == 1


def test_medium_urgency_case():
    result = fuse_evidence(
        SymptomData(severity_score=6, patient_reported_severity="medium"),
        VisionData(
            visual_severity="medium",
            severity_indicators=SeverityIndicators(swelling=True),
        ),
    )

    assert result["urgency"] == "medium"
    assert result["total_risk_score"] == 5


def test_high_urgency_case():
    result = fuse_evidence(
        SymptomData(severity_score=8, patient_reported_severity="high"),
        VisionData(
            visual_severity="high",
            severity_indicators=SeverityIndicators(bleeding=True),
        ),
    )

    assert result["urgency"] == "high"
    assert result["total_risk_score"] == 9


def test_low_patient_severity_and_high_visual_severity_detects_conflict():
    result = fuse_evidence(
        SymptomData(severity_score=2, patient_reported_severity="low"),
        VisionData(
            visual_severity="high",
            severity_indicators=SeverityIndicators(spreading=True),
        ),
    )

    assert result["conflict"]["conflict_detected"] is True
    assert result["conflict"]["conflict_type"] == "severity_mismatch"
    assert result["total_risk_score"] == 7
    assert "Visual evidence suggests higher severity than patient reports" in result["risk_signals"]


def test_worsening_progression_increases_text_score():
    stable = calculate_text_score(
        SymptomData(severity_score=4, progression="stable", patient_reported_severity="medium")
    )
    worsening = calculate_text_score(
        SymptomData(severity_score=4, progression="worsening", patient_reported_severity="medium")
    )

    assert stable == 2
    assert worsening == stable + 2
