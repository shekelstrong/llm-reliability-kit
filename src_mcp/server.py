"""LLM Reliability Kit MCP Server."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src_mcp.tools import parse_response, fallback_chain, select_provider, estimate_cost, retry_with_backoff


app = Server("llm-reliability-kit")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="parse_response",
            description="Парсинг ответа LLM: JSON (включая markdown code-fence), XML, plain text. Robust обработка ошибок.",
            inputSchema={
                "type": "object",
                "properties": {
                    "raw_response": {"type": "string", "description": "Сырой ответ LLM"},
                    "expected_format": {"type": "string", "enum": ["json", "xml", "text", "auto"], "default": "auto"},
                },
                "required": ["raw_response"],
            },
        ),
        Tool(
            name="fallback_chain",
            description="Запрос к LLM с fallback-цепочкой. Если основной провайдер упал — пробует следующий.",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {"type": "array", "items": {"type": "object"}},
                    "providers": {"type": "array", "items": {"type": "string"},
                                  "description": "Список моделей в порядке fallback"},
                },
                "required": ["messages", "providers"],
            },
        ),
        Tool(
            name="select_provider",
            description="Выбор провайдера по cost/latency/quality. Возвращает рекомендованную модель.",
            inputSchema={
                "type": "object",
                "properties": {
                    "priority": {"type": "string", "enum": ["cost", "latency", "quality", "balanced"]},
                    "max_cost_per_1m_tokens": {"type": "number"},
                    "max_latency_ms": {"type": "integer"},
                    "min_quality_score": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["priority"],
            },
        ),
        Tool(
            name="estimate_cost",
            description="Расчёт стоимости запроса: input/output tokens × price per 1M tokens.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {"type": "string"},
                    "input_tokens": {"type": "integer"},
                    "output_tokens": {"type": "integer"},
                },
                "required": ["model", "input_tokens", "output_tokens"],
            },
        ),
        Tool(
            name="retry_with_backoff",
            description="Retry-стратегия для LLM-запросов: exponential backoff с jitter. Обработка rate limit (429), timeout, 5xx.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_retries": {"type": "integer", "default": 3},
                    "initial_delay_ms": {"type": "integer", "default": 1000},
                    "max_delay_ms": {"type": "integer", "default": 30000},
                    "exponential_base": {"type": "number", "default": 2.0},
                },
                "required": ["max_retries"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    import json
    tools_map = {
        "parse_response": parse_response,
        "fallback_chain": fallback_chain,
        "select_provider": select_provider,
        "estimate_cost": estimate_cost,
        "retry_with_backoff": retry_with_backoff,
    }
    try:
        result = await tools_map[name].run(**arguments)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def main():
    async with stdio_server() as (rs, ws):
        await app.run(rs, ws, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
