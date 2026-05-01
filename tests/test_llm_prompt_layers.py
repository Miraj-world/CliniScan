import asyncio
import json

from layers import clinical_reasoning, symptom_structurer
from models.schemas import STANDARD_DISCLAIMER


def test_symptom_structurer_prompt_preserves_json_schema(monkeypatch):
    captured = {}

    async def fake_call_ai(messages, provider, api_key, max_tokens, **_kwargs):
        captured["prompt"] = messages[0]["content"]
        return json.dumps(
            {
                "primary_symptom": "rash",
                "body_location": "left forearm",
                "body_region": "skin",
                "duration_days": 3,
                "severity_score": 4,
                "progression": "worsening",
                "associated_symptoms": ["itching"],
                "patient_reported_severity": "medium",
                "risk_factors": [],
                "text_completeness": 0.8,
            }
        )

    monkeypatch.setattr(symptom_structurer, "call_ai", fake_call_ai)

    result = asyncio.run(
        symptom_structurer.structure_symptoms(
            {
                "symptom_text": "itchy spreading rash",
                "body_location": "left forearm",
                "duration_days": 3,
                "severity_score": 4,
                "age": "not provided",
                "known_conditions": "none",
                "medications": "none",
            },
            provider="anthropic",
            api_key="test-key",
        )
    )

    assert '"primary_symptom"' in captured["prompt"]
    assert "Symptom description: itchy spreading rash" in captured["prompt"]
    assert result["primary_symptom"] == "rash"


def test_clinical_reasoning_prompt_preserves_json_schema(monkeypatch):
    captured = {}

    async def fake_call_ai(messages, provider, api_key, max_tokens, **_kwargs):
        captured["prompt"] = messages[0]["content"]
        return json.dumps(
            {
                "possible_conditions": ["Cellulitis", "Contact dermatitis", "Infected wound"],
                "confidence_levels": ["Medium", "Low", "Low"],
                "clinical_reasoning": [
                    "Visual evidence indicates a higher-severity skin finding.",
                    "Patient-reported symptoms suggest a localized concern.",
                    "The mismatch pattern supports prompt clinical review.",
                ],
                "red_flags": ["Rapid spreading or worsening appearance"],
                "recommendation": "Seek medical attention promptly for in-person evaluation.",
                "disclaimer": STANDARD_DISCLAIMER,
            }
        )

    monkeypatch.setattr(clinical_reasoning, "call_ai", fake_call_ai)

    result = asyncio.run(
        clinical_reasoning.generate_clinical_reasoning(
            {
                "urgency": "high",
                "risk_signals": ["Visual evidence indicates higher severity"],
                "body_region": "skin",
            },
            {"quality_level": "medium"},
            provider="anthropic",
            api_key="test-key",
        )
    )

    assert '"possible_conditions"' in captured["prompt"]
    assert '"urgency": "high"' in captured["prompt"]
    assert result["possible_conditions"] == ["Cellulitis", "Contact dermatitis", "Infected wound"]
    assert result["red_flags"] == ["Rapid spreading or worsening appearance"]
