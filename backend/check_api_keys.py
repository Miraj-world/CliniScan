from __future__ import annotations

import asyncio
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from layers.ai_gateway import ANTHROPIC_MODEL, OPENAI_MODEL, call_ai


ENV_PATH = Path(__file__).resolve().parent / ".env"


async def check_provider(provider: str, env_key: str, model: str) -> bool:
    api_key = os.getenv(env_key, "").strip()
    if not api_key:
        print(f"{provider}: missing {env_key}")
        return False

    try:
        text = await call_ai(
            messages=[{"role": "user", "content": "Reply with only the word OK."}],
            provider=provider,
            api_key=api_key,
            max_tokens=5,
        )
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:300]
        print(f"{provider}: failed ({exc.response.status_code}) using {model}")
        print(detail)
        return False
    except Exception as exc:
        print(f"{provider}: failed using {model}")
        print(str(exc))
        return False

    print(f"{provider}: working using {model} -> {text.strip()!r}")
    return True


async def main() -> int:
    load_dotenv(ENV_PATH)
    results = await asyncio.gather(
        check_provider("anthropic", "ANTHROPIC_API_KEY", ANTHROPIC_MODEL),
        check_provider("openai", "OPENAI_API_KEY", OPENAI_MODEL),
    )
    return 0 if any(results) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
