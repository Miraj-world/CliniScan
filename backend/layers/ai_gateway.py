from __future__ import annotations

from typing import Any

import httpx

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-4-6"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o"


async def _call_anthropic(messages: list[dict[str, Any]], api_key: str, max_tokens: int = 1000, system_prompt: str | None = None) -> str:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system_prompt:
        body["system"] = system_prompt
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(ANTHROPIC_URL, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["content"][0]["text"]


async def _call_openai(messages: list[dict[str, Any]], api_key: str, max_tokens: int = 1000, system_prompt: str | None = None) -> str:
    converted_messages: list[dict[str, Any]] = []
    for message in messages:
        content = message["content"]
        if isinstance(content, str):
            converted_messages.append({"role": message["role"], "content": content})
            continue

        converted_content: list[dict[str, Any]] = []
        for block in content:
            block_type = block.get("type")
            if block_type == "text":
                converted_content.append({"type": "text", "text": block.get("text", "")})
            elif block_type == "image":
                src = block["source"]
                data_url = f"data:{src['media_type']};base64,{src['data']}"
                converted_content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url, "detail": "high"},
                    }
                )

        converted_messages.append({"role": message["role"], "content": converted_content})

    if system_prompt:
        converted_messages.insert(0, {"role": "system", "content": system_prompt})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENAI_MODEL,
        "messages": converted_messages,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(OPENAI_URL, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


async def call_ai(messages: list[dict[str, Any]], provider: str, api_key: str, max_tokens: int = 1000, system_prompt: str | None = None) -> str:
    if provider == "openai":
        return await _call_openai(messages, api_key, max_tokens=max_tokens, system_prompt=system_prompt)
    return await _call_anthropic(messages, api_key, max_tokens=max_tokens, system_prompt=system_prompt)
