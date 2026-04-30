from app.parser import parse_diagnosis_response
from app.schemas import STANDARD_DISCLAIMER


def test_parses_json_wrapped_in_markdown_fences():
    response = """```json
{
  "possible_conditions": ["Contact dermatitis"],
  "confidence_levels": ["High"],
  "urgency": "medium",
  "red_flags": [],
  "recommendation": "Monitor symptoms and seek care if worsening.",
  "clinical_reasoning": ["Structured evidence suggests a localized skin issue."],
  "disclaimer": "Not a diagnosis. Always consult a licensed medical professional."
}
```"""

    result = parse_diagnosis_response(response)

    assert result["possible_conditions"] == ["Contact dermatitis"]
    assert result["confidence_levels"] == ["high"]
    assert result["disclaimer"] == STANDARD_DISCLAIMER


def test_invalid_json_returns_safe_fallback():
    result = parse_diagnosis_response("not valid json")

    assert result["possible_conditions"] == []
    assert result["confidence_levels"] == []
    assert result["urgency"] == "medium"
    assert result["red_flags"] == ["Unable to fully parse AI output"]
    assert result["recommendation"] == "Please consult a licensed medical professional."
    assert result["disclaimer"] == STANDARD_DISCLAIMER


def test_missing_disclaimer_is_added():
    response = """
{
  "possible_conditions": ["Minor burn"],
  "confidence_levels": ["medium"],
  "urgency": "low",
  "red_flags": [],
  "recommendation": "Keep the area clean.",
  "clinical_reasoning": []
}
"""

    result = parse_diagnosis_response(response)

    assert result["disclaimer"] == STANDARD_DISCLAIMER
