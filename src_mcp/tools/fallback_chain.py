"""fallback_chain: запрос с fallback на несколько провайдеров."""

import os
import httpx
import asyncio
import json


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def run(messages: list, providers: list) -> dict:
    """Запрос с fallback.

    Args:
        messages: Список сообщений [{role, content}].
        providers: Список моделей в порядке fallback.

    Returns:
        Словарь с response, used_provider, attempts.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"error": "OPENROUTER_API_KEY not set", "attempts": []}

    attempts = []
    for provider in providers:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    OPENROUTER_URL,
                    json={"model": provider, "messages": messages},
                    headers={"Authorization": f"Bearer {api_key}"},
                )

            if resp.status_code == 200:
                data = resp.json()
                attempts.append({"provider": provider, "status": "success", "http": resp.status_code})
                return {
                    "response": data["choices"][0]["message"]["content"],
                    "used_provider": provider,
                    "attempts": attempts,
                    "model": data.get("model"),
                    "usage": data.get("usage"),
                }
            else:
                attempts.append({"provider": provider, "status": "failed", "http": resp.status_code, "error": resp.text[:200]})
        except Exception as e:
            attempts.append({"provider": provider, "status": "error", "error": str(e)})

    return {"response": None, "used_provider": None, "attempts": attempts, "error": "All providers failed"}
