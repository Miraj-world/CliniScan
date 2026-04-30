import pytest

from app.red_flags import detect_red_flags
from app.schemas import SymptomData


@pytest.mark.parametrize(
    ("symptom_data", "fusion_result", "expected_flag"),
    [
        (
            SymptomData(severity_score=9),
            {},
            "Severe pain reported",
        ),
        (
            SymptomData(associated_symptoms=["rash spreading quickly"]),
            {"risk_signals": ["Spreading pattern detected visually"]},
            "Rapid spreading reported or detected",
        ),
        (
            SymptomData(primary_symptom="rash", associated_symptoms=["fever"]),
            {},
            "Fever with rash reported",
        ),
        (
            SymptomData(body_location="eye", associated_symptoms=["light sensitivity"]),
            {},
            "Eye pain or light sensitivity reported",
        ),
        (
            SymptomData(associated_symptoms=["yellow discharge"]),
            {},
            "Discharge reported or detected",
        ),
        (
            SymptomData(associated_symptoms=["uncontrolled bleeding"]),
            {},
            "Uncontrolled bleeding reported",
        ),
        (
            SymptomData(associated_symptoms=["pus and warm to touch"]),
            {},
            "Signs of infection reported",
        ),
    ],
)
def test_detect_red_flags(symptom_data, fusion_result, expected_flag):
    assert expected_flag in detect_red_flags(symptom_data, fusion_result)
