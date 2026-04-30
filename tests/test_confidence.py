from app.confidence import normalize_confidence, normalize_diagnosis_confidence


def test_normalize_confidence_values():
    assert normalize_confidence("HIGH confidence") == "high"
    assert normalize_confidence("unlikely") == "low"
    assert normalize_confidence("moderate") == "medium"
    assert normalize_confidence(0.9) == "high"
    assert normalize_confidence(25) == "low"


def test_confidence_levels_match_possible_conditions_length():
    result = normalize_diagnosis_confidence(
        {
            "possible_conditions": ["A", "B", "C"],
            "confidence_levels": ["High", "unlikely", "medium", "extra"],
        }
    )

    assert result["confidence_levels"] == ["high", "low", "medium"]


def test_missing_confidence_levels_are_filled_with_medium():
    result = normalize_diagnosis_confidence(
        {
            "possible_conditions": ["A", "B"],
            "confidence_levels": ["low"],
        }
    )

    assert result["confidence_levels"] == ["low", "medium"]
