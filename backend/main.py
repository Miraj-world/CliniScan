from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from layers.clinical_reasoning import generate_clinical_reasoning
from layers.ai_gateway import ANTHROPIC_MODEL, OPENAI_MODEL
from layers.evidence_fusion import fuse_evidence
from layers.json_parser import fallback_diagnosis
from layers.quality_gate import assess_data_quality
from layers.safety_override import run_safety_override
from layers.symptom_structurer import DEFAULT_STRUCTURED_OUTPUT, structure_symptoms
from layers.vision_extractor import extract_vision_features
from models.schemas import AnalyzeRequest, FullResponse, SymptomOutput, VisionOutput

load_dotenv()

app = FastAPI(title="CliniScan", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"


def _provider_key(provider: str) -> str:
    if provider == "openai":
        value = os.getenv("OPENAI_API_KEY", "").strip()
        if not value:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not configured on server")
        return value

    value = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not value:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY is not configured on server")
    return value


def _load_demo_cache(scenario: int) -> dict:
    path = CACHE_DIR / f"scenario_{scenario}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Demo scenario {scenario} is not available")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Demo cache is invalid for scenario {scenario}: {exc}")


def _default_fusion_output(symptom_output: dict, no_image_mode: bool, override: dict) -> dict:
    urgency = "high" if override.get("override_triggered") else "medium"
    return {
        "vision_score": 0.0,
        "text_score": 0.0,
        "total_risk_score": 0.0,
        "urgency": urgency,
        "conflict": {
            "conflict_detected": False,
            "conflict_type": None,
            "text_severity": symptom_output.get("patient_reported_severity", "low"),
            "vision_severity": None if no_image_mode else "low",
            "visual_dominates": False,
        },
        "risk_signals": [
            "Fusion fallback engaged due to a processing error",
            *[
                f"Critical keyword detected: '{item}'"
                for item in override.get("triggered_by", [])
            ],
        ],
        "body_region": symptom_output.get("body_region", "other"),
        "no_image_mode": no_image_mode,
    }


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    if req.demo_scenario in (1, 2, 3):
        cached = _load_demo_cache(req.demo_scenario)
        try:
            return FullResponse.model_validate(cached).model_dump()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Demo cache schema mismatch: {exc}")

    provider = req.provider
    api_key = _provider_key(provider)

    override = run_safety_override(req.symptom_text)

    form_data = {
        "symptom_text": req.symptom_text,
        "body_location": req.body_location,
        "duration_days": req.duration_days,
        "severity_score": req.severity_score,
        "age": req.age if req.age is not None else "not provided",
        "known_conditions": req.known_conditions or "none",
        "medications": req.medications or "none",
    }

    symptom_output = dict(DEFAULT_STRUCTURED_OUTPUT)
    symptom_output["body_location"] = req.body_location
    symptom_output["duration_days"] = req.duration_days
    symptom_output["severity_score"] = req.severity_score
    symptom_output["patient_reported_severity"] = (
        "low" if req.severity_score <= 3 else "medium" if req.severity_score <= 6 else "high"
    )

    # Strip data URI prefix if present (e.g., "data:image/jpeg;base64,")
    image_data = req.image_base64 or ""
    if ";base64," in image_data:
        image_data = image_data.split(";base64,")[1]

    # Strip data URI prefix if present (e.g., "data:image/jpeg;base64,")
    image_data = req.image_base64 or ""
    if ";base64," in image_data:
        image_data = image_data.split(";base64,")[1]

    vision_output: dict = {}
    no_image_mode = not bool(image_data)
    no_image_reason = "no_image_provided" if no_image_mode else None

    if not no_image_mode:
        vision_task = asyncio.create_task(
            extract_vision_features(image_data, req.image_mime, provider, api_key)
        )
        symptom_task = asyncio.create_task(structure_symptoms(form_data, provider, api_key))

        vision_result, symptom_result = await asyncio.gather(vision_task, symptom_task, return_exceptions=True)

        if isinstance(symptom_result, Exception):
            symptom_output = dict(DEFAULT_STRUCTURED_OUTPUT)
            symptom_output["body_location"] = req.body_location
            symptom_output["duration_days"] = req.duration_days
            symptom_output["severity_score"] = req.severity_score
            symptom_output["text_completeness"] = 0.25
        else:
            symptom_output = symptom_result

        if isinstance(vision_result, Exception):
            no_image_mode = True
            vision_output = {}
            no_image_reason = "vision_processing_error"
        else:
            if not vision_result.get("medical_relevance", True):
                no_image_mode = True
                vision_output = {}
                no_image_reason = "image_not_medically_relevant"
            else:
                vision_output = vision_result
                no_image_reason = None
    else:
        try:
            symptom_output = await structure_symptoms(form_data, provider, api_key)
        except Exception:
            symptom_output = dict(DEFAULT_STRUCTURED_OUTPUT)
            symptom_output["body_location"] = req.body_location
            symptom_output["duration_days"] = req.duration_days
            symptom_output["severity_score"] = req.severity_score
            symptom_output["text_completeness"] = 0.25

    try:
        symptom_output = SymptomOutput.model_validate(symptom_output).model_dump()
    except Exception:
        symptom_output = SymptomOutput.model_validate(DEFAULT_STRUCTURED_OUTPUT).model_dump()

    if vision_output:
        try:
            vision_output = VisionOutput.model_validate(vision_output).model_dump()
        except Exception:
            no_image_mode = True
            vision_output = {}
            no_image_reason = "vision_schema_validation_error"

    try:
        fusion_output = fuse_evidence(symptom_output, vision_output, override, no_image=no_image_mode)
    except Exception:
        fusion_output = _default_fusion_output(symptom_output, no_image_mode, override)

    try:
        quality_output = assess_data_quality(vision_output, symptom_output, no_image_mode)
    except Exception:
        quality_output = {
            "quality_score": 0.5,
            "quality_level": "medium",
            "show_uncertain_badge": True,
        }

    try:
        diagnosis = await generate_clinical_reasoning(fusion_output, quality_output, provider, api_key)
    except Exception:
        diagnosis = fallback_diagnosis()
        fusion_output["risk_signals"] = list(dict.fromkeys([
            *fusion_output.get("risk_signals", []),
            "Clinical reasoning model response was unavailable or invalid",
        ]))

    payload = {
        "pipeline_stages": {
            "safety_override": override,
            "vision_output": vision_output,
            "symptom_output": symptom_output,
            "fusion_output": fusion_output,
            "quality_output": quality_output,
        },
        "diagnosis": diagnosis,
        "urgency": fusion_output.get("urgency", "medium"),
        "conflict": fusion_output.get("conflict", {}),
        "risk_signals": fusion_output.get("risk_signals", []),
        "quality": quality_output,
        "no_image_mode": no_image_mode,
        "no_image_reason": no_image_reason,
        "demo_mode": False,
    }

    try:
        return FullResponse.model_validate(payload).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Response schema validation failed: {exc}")


@app.get("/health")
async def health():
    anthropic_ready = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
    openai_ready = bool(os.getenv("OPENAI_API_KEY", "").strip())
    return {
        "status": "ok",
        "providers": {
            "anthropic": {"configured": anthropic_ready, "model": ANTHROPIC_MODEL},
            "openai": {"configured": openai_ready, "model": OPENAI_MODEL},
        },
    }
