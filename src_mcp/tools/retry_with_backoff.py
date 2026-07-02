"""retry_with_backoff: retry-стратегия с exponential backoff и jitter."""

import random
import asyncio
import httpx


async def run(max_retries: int, initial_delay_ms: int = 1000, max_delay_ms: int = 30000, exponential_base: float = 2.0) -> dict:
    """Генерирует план retry с jitter.

    Args:
        max_retries: Макс кол-во попыток.
        initial_delay_ms: Начальная задержка (мс).
        max_delay_ms: Макс задержка (мс).
        exponential_base: База экспоненты.

    Returns:
        Словарь с delays и примерами.
    """
    delays = []
    for i in range(max_retries):
        # base * exponential_base^i, capped at max
        base_delay = min(initial_delay_ms * (exponential_base ** i), max_delay_ms)
        # jitter ±25%
        jitter = base_delay * 0.25
        delay_ms = base_delay + random.uniform(-jitter, jitter)
        delays.append(round(delay_ms))

    return {
        "strategy": "exponential backoff with jitter",
        "max_retries": max_retries,
        "delays_ms": delays,
        "total_max_wait_ms": sum(delays),
        "handles": ["429 rate limit", "5xx server error", "timeout", "connection reset"],
        "skips": ["4xx client error (don't retry)", "401/403 (auth issue)"],
    }
