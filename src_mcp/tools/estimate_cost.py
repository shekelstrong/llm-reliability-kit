"""estimate_cost: расчёт стоимости LLM-запроса."""


# Цены за 1M tokens (USD)
PRICES = {
    "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
    "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
    "openai/gpt-4o": {"input": 2.5, "output": 10.0},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "google/gemini-2.5-pro": {"input": 1.25, "output": 5.0},
    "google/gemini-2.5-flash": {"input": 0.075, "output": 0.3},
    "meta-llama/llama-3.1-70b-instruct": {"input": 0.59, "output": 0.79},
}


async def run(model: str, input_tokens: int, output_tokens: int) -> dict:
    """Считает стоимость.

    Args:
        model: Модель.
        input_tokens: Кол-во input tokens.
        output_tokens: Кол-во output tokens.

    Returns:
        Словарь с breakdown и total.
    """
    prices = PRICES.get(model)
    if not prices:
        return {"error": f"Unknown model: {model}", "available": list(PRICES.keys())}

    cost_input = (input_tokens / 1_000_000) * prices["input"]
    cost_output = (output_tokens / 1_000_000) * prices["output"]
    total = cost_input + cost_output

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_input_usd": round(cost_input, 6),
        "cost_output_usd": round(cost_output, 6),
        "total_usd": round(total, 6),
        "total_rub": round(total * 95, 2),  # примерный курс
        "price_per_1m": prices,
    }
