"""OpenAI-compatible Chat Completions HTTP client."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any


def endpoint_url(base_url: str) -> str:
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def extract_content(payload: dict[str, Any]) -> str:
    try:
        message = payload["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("模型接口响应结构不兼容，请检查 AI_BASE_URL 和模型名称。") from exc
    content = message.get("content", "") if isinstance(message, dict) else ""
    if isinstance(content, list):
        content = "".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content)
    return str(content)


def request_chat_completion(
    messages: list[dict[str, str]],
    *,
    api_key: str,
    base_url: str,
    model: str,
    timeout: int,
    temperature: float,
    max_tokens: int,
    json_mode: bool = True,
    logger: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    request = urllib.request.Request(
        endpoint_url(base_url),
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    log = logger or (lambda _message: None)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            choice = payload.get("choices", [{}])[0]
            message = choice.get("message", {}) if isinstance(choice, dict) else {}
            content = message.get("content", "") if isinstance(message, dict) else ""
            log(
                f"DeepSeek success elapsed={time.monotonic() - started:.2f}s "
                f"finish={choice.get('finish_reason', '') if isinstance(choice, dict) else ''} "
                f"content_chars={len(str(content))} json_mode={json_mode}"
            )
            return payload
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(detail)
            detail = parsed.get("error", {}).get("message", detail)
        except json.JSONDecodeError:
            pass
        log(f"DeepSeek HTTP {exc.code} elapsed={time.monotonic() - started:.2f}s detail={detail[:160]}")
        raise RuntimeError(f"DeepSeek接口返回 {exc.code}，请稍后重试。") from exc
    except urllib.error.URLError as exc:
        log(f"DeepSeek connection error elapsed={time.monotonic() - started:.2f}s reason={exc.reason}")
        raise RuntimeError("DeepSeek连接超时或网络不可用，请稍后重试。") from exc
    except TimeoutError as exc:
        log(f"DeepSeek timeout elapsed={time.monotonic() - started:.2f}s")
        raise RuntimeError("DeepSeek响应超时，请稍后重试。") from exc
