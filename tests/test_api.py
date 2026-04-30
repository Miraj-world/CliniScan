import json

from fastapi.testclient import TestClient

from app import main
from app.schemas import STANDARD_DISCLAIMER


def test_health_endpoint_returns_status_and_models():
    client = TestClient(main.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "models": {
            "anthropic": main.ANTHROPIC_MODEL,
            "openai": main.OPENAI_MODEL,
        },
    }


def test_analyze_text_only_endpoint_uses_structured_pipeline(monkeypatch):
    ai_responses = iter(
        [
            json.dumps(
                {
                    "primary_symptom": "itchy rash",
                    "body_location": "left forearm",
                    "duration_days": 2,
                    "severity_score": 3,
                    "progression": "stable",
                    "associated_symptoms": ["itching"],
                    "patient_reported_severity": "low",
                    "risk_factors": [],
                }
            ),
            json.dumps(
                {
                    "possible_conditions": ["Contact dermatitis"],
                    "confidence_levels": ["medium"],
                    "urgency": "low",
                    "red_flags": [],
                    "recommendation": "Keep the area clean and monitor symptoms.",
                    "clinical_reasoning": [
                        "Structured evidence suggests a mild localized skin issue."
                    ],
                    "disclaimer": STANDARD_DISCLAIMER,
                }
            ),
        ]
    )

    async def fake_call_ai(messages, api_key, provider, max_tokens=1024):
        return next(ai_responses)

    monkeypatch.setattr(main, "_call_ai", fake_call_ai)
    client = TestClient(main.app)

    response = client.post(
        "/analyze",
        json={
            "symptom_text": "Itchy red rash on my arm",
            "body_location": "left forearm",
            "duration_days": 2,
            "severity": 3,
            "api_key": "test-key",
            "provider": "openai",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["has_image"] is False
    assert body["provider"] == "openai"
    assert body["fusion"]["urgency"] == "low"
    assert body["fusion"]["vision_score"] == 0
    assert body["diagnosis"]["possible_conditions"] == ["Contact dermatitis"]
    assert body["diagnosis"]["disclaimer"] == STANDARD_DISCLAIMER
