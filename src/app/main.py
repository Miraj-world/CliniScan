"""
SymptomScan AI — FastAPI entry point
Place this file at: src/main.py
Run with: python -m uvicorn src.main:app --reload  (from the CliniScan folder)

Supports: Anthropic (Claude) and OpenAI (GPT-4o)
"""

from __future__ import annotations

import json
import re
from typing import Literal, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.fusion import fuse_evidence
from app.parser import safe_parse_diagnosis_response
from app.prompts import DIAGNOSIS_PROMPT, SYMPTOM_STRUCTURER_PROMPT
from app.red_flags import detect_red_flags
from app.schemas import (
    STANDARD_DISCLAIMER,
    SeverityIndicators,
    SymptomData,
    VisionData,
)

# ── App setup ──────────────────────────────────────────────────────────────────

app = FastAPI(title="SymptomScan AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Model config ───────────────────────────────────────────────────────────────

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o"

# ── Vision prompt ──────────────────────────────────────────────────────────────

VISION_PROMPT = """You are a clinical image analysis assistant.
Analyze this image and return ONLY a valid JSON object. No markdown, no explanation.

{
  "visual_features": {
    "primary_color": "",
    "texture": "",
    "shape": "",
    "spread_pattern": "",
    "border_definition": "defined | diffuse | irregular"
  },
  "detected_signs": [],
  "severity_indicators": {
    "open_wound": false,
    "bleeding": false,
    "swelling": false,
    "spreading": false,
    "discoloration": false,
    "discharge": false
  },
  "visual_severity": "low | medium | high",
  "confidence": "low | medium | high"
}

detected_signs: plain English observations only. Never diagnose."""

# ── Request model ──────────────────────────────────────────────────────────────


class AnalyzeRequest(BaseModel):
    symptom_text: str
    body_location: str
    duration_days: int = 1
    severity: int = 5
    age: Optional[int] = None
    known_conditions: Optional[str] = None
    image_base64: Optional[str] = None
    image_mime: Optional[str] = "image/jpeg"
    api_key: str
    provider: Literal["anthropic", "openai"] = "anthropic"

# ── JSON helper ────────────────────────────────────────────────────────────────


def _parse_json(text: str) -> dict:
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    start, end = clean.find("{"), clean.rfind("}")
    if start != -1 and end != -1:
        clean = clean[start:end + 1]
    return json.loads(clean)

# ── Anthropic caller ───────────────────────────────────────────────────────────


async def _call_anthropic(messages: list, api_key: str, max_tokens: int = 1024) -> str:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {"model": ANTHROPIC_MODEL,
            "max_tokens": max_tokens, "messages": messages}
    async with httpx.AsyncClient(timeout=40) as client:
        resp = await client.post(ANTHROPIC_URL, headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

# ── OpenAI caller ──────────────────────────────────────────────────────────────


async def _call_openai(messages: list, api_key: str, max_tokens: int = 1024) -> str:
    """
    Converts Anthropic-style message format to OpenAI format.
    Anthropic image: { type: image, source: { type: base64, media_type, data } }
    OpenAI image:    { type: image_url, image_url: { url: data:mime;base64,... } }
    """
    openai_messages = []
    for msg in messages:
        content = msg["content"]
        if isinstance(content, str):
            openai_messages.append({"role": msg["role"], "content": content})
            continue
        converted = []
        for block in content:
            if block["type"] == "text":
                converted.append({"type": "text", "text": block["text"]})
            elif block["type"] == "image":
                src = block["source"]
                data_url = f"data:{src['media_type']};base64,{src['data']}"
                converted.append({
                    "type": "image_url",
                    "image_url": {"url": data_url, "detail": "high"},
                })
        openai_messages.append({"role": msg["role"], "content": converted})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {"model": OPENAI_MODEL, "max_tokens": max_tokens,
            "messages": openai_messages}
    async with httpx.AsyncClient(timeout=40) as client:
        resp = await client.post(OPENAI_URL, headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

# ── Unified AI caller ──────────────────────────────────────────────────────────


async def _call_ai(messages: list, api_key: str, provider: str, max_tokens: int = 1024) -> str:
    if provider == "openai":
        return await _call_openai(messages, api_key, max_tokens)
    return await _call_anthropic(messages, api_key, max_tokens)

# ── Main endpoint ──────────────────────────────────────────────────────────────


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    provider = req.provider

    # Step 1: Vision branch
    if req.image_base64:
        vision_messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": req.image_mime,
                            "data": req.image_base64,
                        },
                    },
                    {"type": "text", "text": VISION_PROMPT},
                ],
            }
        ]
        try:
            vision_raw = await _call_ai(vision_messages, req.api_key, provider)
            vision_data = VisionData.model_validate(_parse_json(vision_raw))
        except Exception as e:
            raise HTTPException(
                status_code=502, detail=f"Vision API error: {e}")
    else:
        vision_data = VisionData(
            severity_indicators=SeverityIndicators(),
            visual_severity="low",
            confidence="low",
        )

    # Step 2: Symptom structurer
    user_text = (
        f"Symptom: {req.symptom_text}. "
        f"Location: {req.body_location}. "
        f"Duration: {req.duration_days} days. "
        f"Severity: {req.severity}/10."
    )
    if req.age:
        user_text += f" Age: {req.age}."
    if req.known_conditions:
        user_text += f" Known conditions: {req.known_conditions}."

    try:
        symptom_raw = await _call_ai(
            [{"role": "user", "content": SYMPTOM_STRUCTURER_PROMPT.format(
                user_text=user_text)}],
            req.api_key, provider,
        )
        symptom_data = SymptomData.model_validate(_parse_json(symptom_raw))
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Symptom structurer error: {e}")

    # Step 3: Evidence fusion — Isaac's pure Python code
    fusion_dict = fuse_evidence(symptom_data, vision_data)

    # Step 4: Red flag detection — Isaac's red_flags.py
    extra_flags = detect_red_flags(symptom_data, fusion_dict)

    # Step 5: Clinical reasoning
    try:
        diagnosis_raw = await _call_ai(
            [{"role": "user", "content": DIAGNOSIS_PROMPT.format(
                fusion_output=json.dumps(fusion_dict, indent=2))}],
            req.api_key, provider, max_tokens=1500,
        )
        diagnosis_dict = safe_parse_diagnosis_response(diagnosis_raw)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Diagnosis error: {e}")

    # Merge red flags from both sources
    all_flags = list(dict.fromkeys(
        extra_flags + (diagnosis_dict.get("red_flags") or [])))
    diagnosis_dict["red_flags"] = all_flags
    diagnosis_dict.setdefault("disclaimer", STANDARD_DISCLAIMER)

    return {
        "fusion": fusion_dict,
        "diagnosis": diagnosis_dict,
        "has_image": req.image_base64 is not None,
        "provider": provider,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "models": {"anthropic": ANTHROPIC_MODEL, "openai": OPENAI_MODEL}}
