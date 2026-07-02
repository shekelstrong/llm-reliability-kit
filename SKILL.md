---
name: llm-reliability-kit
description: Надёжность LLM-приложений. Парсинг ответов (JSON/XML/text), fallback-цепочки провайдеров, выбор по cost/latency/quality, расчёт стоимости, retry с exponential backoff.
---

# LLM Reliability Kit

MCP-сервер для production-ready LLM-приложений.

## Когда использовать

- Строишь LLM-агент / RAG-бот / AI-приложение
- Нужна надёжность (fallback если провайдер упал)
- Нужно считать юнит-экономику
- Нужно парсить нестабильные ответы LLM
- Нужен retry с правильной стратегией

## 5 tools

```
ответ LLM → parse_response → бизнес-логика
           ↑
           fallback_chain (Claude → GPT-4o → Gemini)
           ↑
           retry_with_backoff (429, 5xx, timeout)
```

## Алгоритм

### 1. parse_response
Robust парсинг ответа LLM:
- Убирает ```json markdown fence
- Ищет JSON блок в произвольном тексте
- Auto-fix типичных багов (одинарные → двойные кавычки, None → null)

### 2. fallback_chain
Запрос к LLM с автоматическим переключением:
- Принимает список `providers: ["claude-3.5-sonnet", "gpt-4o", "gemini-2.5-pro"]`
- Пробует первый, при ошибке переходит к следующему
- Возвращает `used_provider` + лог `attempts`

### 3. select_provider
Выбор оптимальной модели по приоритетам:
- **cost** — самая дешёвая (gemini-flash, gpt-4o-mini, claude-haiku)
- **latency** — самая быстрая
- **quality** — самая качественная (claude-3.5-sonnet, gpt-4o)
- **balanced** — формула `quality / (cost_normalized + latency_normalized)`

Фильтры: `max_cost_per_1m_tokens`, `max_latency_ms`, `min_quality_score`.

### 4. estimate_cost
Считает стоимость запроса:
- Вход: модель + input_tokens + output_tokens
- Возвращает: cost_input_usd, cost_output_usd, total_usd, total_rub (×95)

### 5. retry_with_backoff
Стратегия retry:
- Exponential backoff: delay = base * exp^i
- Jitter ±25% (защита от thundering herd)
- Handles: 429, 5xx, timeout, connection reset
- Skips: 4xx (client error), 401/403 (auth)

## Pitfalls

| Ошибка | Последствие | Как избежать |
|---|---|---|
| Парсить JSON напрямую | Упадёт на ```json fence | parse_response |
| Один провайдер | Падение = downtime | fallback_chain |
| Считать $/1M tokens забыть | Счёт в 100x дороже | estimate_cost |
| Retry без backoff | Ban от API | retry_with_backoff |
| Retry 4xx | Бессмысленно | skip client errors |
| OpenAI / Anthropic напрямую | Vendor lock | OpenRouter |

## Источники

4 скилла: llm-response-parsing, llm-inference-ops, gen-ai-provider-ops, huggingface-hub.
