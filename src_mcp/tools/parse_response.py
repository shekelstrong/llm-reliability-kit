"""parse_response: парсинг ответа LLM (JSON/XML/text)."""

import json
import re
import xml.etree.ElementTree as ET


async def run(raw_response: str, expected_format: str = "auto") -> dict:
    """Парсит ответ LLM.

    Args:
        raw_response: Сырой ответ.
        expected_format: json/xml/text/auto.

    Returns:
        Словарь с parsed, format_detected, errors.
    """
    errors = []
    text = raw_response.strip()

    if expected_format == "auto":
        # Пробуем JSON
        if text.startswith("{") or text.startswith("["):
            expected_format = "json"
        elif text.startswith("<"):
            expected_format = "xml"
        elif text.startswith("```"):
            # markdown code fence — определяем по языку
            fence_lang_match = re.match(r"^```(\w+)?", text)
            fence_lang = fence_lang_match.group(1) if fence_lang_match else None
            if fence_lang in ("json", None):
                expected_format = "json"
            elif fence_lang == "xml":
                expected_format = "xml"
            else:
                expected_format = "text"
        else:
            expected_format = "text"

    if expected_format == "json":
        # 1. Убираем markdown code fence
        text_clean = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text_clean = re.sub(r"\n?```\s*$", "", text_clean)
        text_clean = text_clean.strip()

        # 2. Прямой JSON
        try:
            return {"parsed": json.loads(text_clean), "format_detected": "json", "errors": []}
        except json.JSONDecodeError:
            pass

        # 3. Ищем JSON блок в тексте
        json_match = re.search(r"\{[\s\S]*\}", text_clean)
        if json_match:
            try:
                return {"parsed": json.loads(json_match.group(0)), "format_detected": "json (extracted)", "errors": []}
            except json.JSONDecodeError as e:
                errors.append(f"JSON parse error: {e}")

        # 4. Пробуем с починкой типичных багов
        fixed = text_clean.replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false")
        try:
            return {"parsed": json.loads(fixed), "format_detected": "json (auto-fixed)", "warnings": ["auto-replaced single quotes"], "errors": []}
        except json.JSONDecodeError:
            pass

        return {"parsed": None, "format_detected": "json", "errors": errors or ["Could not parse JSON"]}

    if expected_format == "xml":
        try:
            root = ET.fromstring(text)
            return {"parsed": ET.tostring(root, encoding="unicode"), "format_detected": "xml", "errors": []}
        except ET.ParseError as e:
            return {"parsed": None, "format_detected": "xml", "errors": [f"XML parse error: {e}"]}

    # text
    return {"parsed": text, "format_detected": "text", "errors": []}
