"""select_provider: выбор провайдера по приоритетам."""


# Модели с метриками (обновляются вручную)
MODELS = {
    "anthropic/claude-3.5-sonnet": {"cost_in": 3.0, "cost_out": 15.0, "latency_ms": 1500, "quality": 0.92, "context": 200000},
    "anthropic/claude-3-haiku": {"cost_in": 0.25, "cost_out": 1.25, "latency_ms": 800, "quality": 0.78, "context": 200000},
    "openai/gpt-4o": {"cost_in": 2.5, "cost_out": 10.0, "latency_ms": 1200, "quality": 0.91, "context": 128000},
    "openai/gpt-4o-mini": {"cost_in": 0.15, "cost_out": 0.6, "latency_ms": 700, "quality": 0.82, "context": 128000},
    "google/gemini-2.5-pro": {"cost_in": 1.25, "cost_out": 5.0, "latency_ms": 1400, "quality": 0.89, "context": 1000000},
    "google/gemini-2.5-flash": {"cost_in": 0.075, "cost_out": 0.3, "latency_ms": 600, "quality": 0.80, "context": 1000000},
    "meta-llama/llama-3.1-70b-instruct": {"cost_in": 0.59, "cost_out": 0.79, "latency_ms": 1100, "quality": 0.85, "context": 131000},
}


async def run(priority: str, max_cost_per_1m_tokens: float = None, max_latency_ms: int = None, min_quality_score: float = None) -> dict:
    """Выбирает провайдера.

    Args:
        priority: cost/latency/quality/balanced.
        max_cost_per_1m_tokens: Макс $/1M tokens (input+output avg).
        max_latency_ms: Макс латентность.
        min_quality_score: Мин качество (0-1).

    Returns:
        Словарь с recommended, alternatives, reasoning.
    """
    candidates = []

    for model, m in MODELS.items():
        if max_cost_per_1m_tokens and (m["cost_in"] + m["cost_out"]) / 2 > max_cost_per_1m_tokens:
            continue
        if max_latency_ms and m["latency_ms"] > max_latency_ms:
            continue
        if min_quality_score and m["quality"] < min_quality_score:
            continue
        candidates.append({"model": model, **m})

    if not candidates:
        return {"recommended": None, "alternatives": [], "reasoning": "No models match filters"}

    if priority == "cost":
        candidates.sort(key=lambda c: c["cost_in"] + c["cost_out"])
    elif priority == "latency":
        candidates.sort(key=lambda c: c["latency_ms"])
    elif priority == "quality":
        candidates.sort(key=lambda c: -c["quality"])
    else:  # balanced
        candidates.sort(key=lambda c: -(c["quality"] / ((c["cost_in"] + c["cost_out"]) / 10 + c["latency_ms"] / 1000)))

    return {
        "recommended": candidates[0],
        "alternatives": candidates[1:4],
        "reasoning": f"Сортировка по: {priority}. Топ-1: {candidates[0]['model']}",
        "total_candidates": len(candidates),
    }
