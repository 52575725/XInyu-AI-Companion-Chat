"""Validation and size limits for chat API payloads."""

from __future__ import annotations

from typing import Any


def _bounded_state(value: Any, *, depth: int = 0) -> Any:
    if depth >= 4:
        return ""
    if isinstance(value, str):
        return value.strip()[:500]
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, list):
        return [_bounded_state(item, depth=depth + 1) for item in value[-20:]]
    if isinstance(value, dict):
        return {
            str(key)[:40]: _bounded_state(item, depth=depth + 1)
            for key, item in list(value.items())[:30]
        }
    return str(value).strip()[:500]


def _bounded_text_list(value: Any, limit: int, item_chars: int = 160) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip()[:item_chars] for item in value[-limit:] if str(item).strip()]


def sanitize_chat_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Keep direct API callers inside the same bounds as the browser client."""
    if not isinstance(data, dict):
        raise ValueError("请求格式错误")
    latest = str(data.get("latest_message", "")).strip()
    if not latest:
        raise ValueError("消息内容不能为空")

    clean = dict(data)
    clean["latest_message"] = latest[:2000]
    try:
        clean["turns"] = max(0, min(int(data.get("turns", 0) or 0), 10_000))
    except (TypeError, ValueError):
        clean["turns"] = 0
    try:
        clean["scene_age_turns"] = max(0, min(int(data.get("scene_age_turns", 0) or 0), 10_000))
    except (TypeError, ValueError):
        clean["scene_age_turns"] = 0

    history: list[dict[str, str]] = []
    messages = data.get("messages", [])
    if isinstance(messages, list):
        for item in messages[-40:]:
            if not isinstance(item, dict) or item.get("role") not in {"user", "assistant", "narration"}:
                continue
            text = str(item.get("text", "")).strip()[:2000]
            if text:
                history.append({"role": str(item["role"]), "text": text})
    clean["messages"] = history

    list_limits = {
        "memories": (20, 240),
        "topics": (80, 160),
        "recent_topics": (60, 160),
        "recent_topic_domains": (32, 80),
        "recent_moves": (40, 160),
        "recent_patterns": (20, 80),
        "recent_initiatives": (20, 80),
        "recent_topic_sources": (24, 80),
        "recent_story_beats": (32, 240),
        "recent_reply_openings": (80, 160),
        "recent_locations": (10, 120),
        "recent_suggestions": (60, 240),
    }
    for key, (limit, chars) in list_limits.items():
        clean[key] = _bounded_text_list(data.get(key), limit, chars)
    for key in ("relationship", "scene", "arc", "life"):
        clean[key] = _bounded_state(data.get(key, {})) if isinstance(data.get(key, {}), dict) else {}
    clean["character_id"] = str(data.get("character_id", "")).strip()[:64]
    clean["scenario_id"] = str(data.get("scenario_id", "")).strip()[:64]
    clean["memory_id"] = str(data.get("memory_id", "")).strip()[:64]
    clean["mature_mode"] = data.get("mature_mode") is True
    clean["adult_confirmed"] = data.get("adult_confirmed") is True
    return clean
