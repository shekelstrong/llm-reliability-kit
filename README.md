# llm-reliability-kit

> MCP-сервер для надёжной работы с LLM: парсинг ответов, fallback-цепочки, выбор провайдера, расчёт стоимости, retry-стратегии.

[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![MCP](https://img.shields.io/badge/MCP-compatible-purple.svg)](https://modelcontextprotocol.io)

## 🎯 Что это

MCP-сервер с 5 инструментами для надёжных LLM-приложений:

- 🔍 **parse_response** — парсинг ответа (JSON/XML/text, обработка markdown code-fence, auto-fix)
- 🔄 **fallback_chain** — цепочка провайдеров (Claude → GPT-4o → Gemini)
- 🎯 **select_provider** — выбор по cost/latency/quality
- 💰 **estimate_cost** — расчёт стоимости в USD и рублях
- ⏱ **retry_with_backoff** — exponential backoff с jitter

## 📦 Установка

```bash
git clone https://github.com/shekelstrong/llm-reliability-kit.git
cd llm-reliability-kit
pip install -r requirements.txt
export OPENROUTER_API_KEY=sk-or-v1-...
```

## 🛠 MCP Tools

### parse_response
```python
result = await parse_response.run('```json\n{"score": 95}\n```', expected_format="auto")
# → {parsed: {"score": 95}, format_detected: "json", errors: []}
```

**Особенности:**
- Убирает markdown code fence (```json)
- Ищет JSON блок в произвольном тексте
- Auto-fix типичных багов (одинарные кавычки, None → null)

### fallback_chain
```python
result = await fallback_chain.run(
    messages=[{"role": "user", "content": "Hello"}],
    providers=["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "google/gemini-2.5-pro"]
)
# → {response: "...", used_provider: "...", attempts: [...]}
```

Если первый упал — пробует следующий. Возвращает лог попыток.

### select_provider
```python
result = await select_provider.run(
    priority="balanced",
    max_cost_per_1m_tokens=5.0,
    min_quality_score=0.85
)
# → {recommended: {...}, alternatives: [...], reasoning: "..."}
```

7 моделей в базе (Claude 3.5 Sonnet, GPT-4o, Gemini 2.5 Pro, Llama 3.1, ...).

### estimate_cost
```python
result = await estimate_cost.run(
    model="anthropic/claude-3.5-sonnet",
    input_tokens=1500,
    output_tokens=500
)
# → {total_usd: 0.012, total_rub: 1.14, ...}
```

### retry_with_backoff
```python
result = await retry_with_backoff.run(
    max_retries=3,
    initial_delay_ms=1000,
    exponential_base=2.0
)
# → {delays_ms: [1000, 2000, 4000], handles: ["429", "5xx", ...], skips: ["4xx", "401"]}
```

## 📁 Структура

```
llm-reliability-kit/
├── README.md
├── LICENSE
├── SKILL.md
├── requirements.txt
├── src_mcp/
│   ├── server.py
│   └── tools/
│       ├── parse_response.py
│       ├── fallback_chain.py
│       ├── select_provider.py
│       ├── estimate_cost.py
│       └── retry_with_backoff.py
└── .github/workflows/ci.yml
```

## 📄 License

MIT © Vasiliy Nedopekin (shekelstrong)
