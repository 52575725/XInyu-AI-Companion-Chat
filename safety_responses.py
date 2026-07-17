"""Deterministic public-demo safety responses for high-risk user messages."""

from __future__ import annotations

import re
from typing import Any


SELF_HARM_PATTERN = re.compile(
    r"(?:我|自己).{0,12}(?:自杀|不想活|活不下去|结束生命|伤害自己|伤害我自己|割腕|吞药|跳楼)"
    r"|(?:控制不住|忍不住).{0,8}(?:伤害自己|伤害我自己|自残)"
    r"|(?:已经|正在).{0,6}(?:割腕|吞药|自残|伤害自己)"
)
HARM_OTHERS_PATTERN = re.compile(
    r"(?:我|现在).{0,10}(?:想杀人|想伤害别人|要伤害别人|控制不住要打人|准备报复)"
)
AGE_PATTERN = re.compile(r"(?:我|本人)?\s*(?:才|只有)?\s*(\d{1,2})\s*岁")
DEPENDENCY_PATTERN = re.compile(
    r"(?:我)?只需要你|只有你(?:会|能|愿意)?(?:陪|懂|要)我|"
    r"我不需要(?:现实里的|其他)?(?:朋友|家人|任何人)|你比现实中的人更重要|为了你疏远"
)


def _base_result(reply: str, suggestions: list[str], *, topic: str) -> dict[str, Any]:
    return {
        "reply": reply,
        "narration": "",
        "suggestions": suggestions,
        "memory_updates": [],
        "topic": topic,
        "conversation_move": "安全回应",
        "interaction_pattern": "情绪承接",
        "topic_domain": "生活目标",
        "initiative": "自然回应",
        "topic_source": "用户当前话语",
        "affinity_update": {
            "delta": 0,
            "reason": "安全场景不计算好感变化",
            "reaction": "中立",
            "trigger": "普通交流",
        },
        "arc_update": {
            "phase": "试探",
            "central_conflict": "",
            "shared_goal": "",
            "last_beat": "暂停剧情并优先确认现实安全",
            "tension_delta": 0,
            "trust_delta": 0,
            "resolved": False,
        },
        "scene_update": {
            "location": "", "time": "", "activity": "",
            "add_props": [], "remove_props": [],
            "add_open_loops": [], "close_open_loops": [],
        },
        "life_update": {
            "current_goal": "", "current_problem": "",
            "next_plan": "", "recent_event": "",
        },
        "user_message_type": "dialogue",
        "user_action_narration": "",
    }


def build_safety_response(data: dict[str, Any]) -> dict[str, Any] | None:
    latest = str(data.get("latest_message", "")).strip()
    if SELF_HARM_PATTERN.search(latest):
        return _base_result(
            "先把现实安全放在第一位。请现在远离可能伤害自己的物品，去有其他人在的地方，并立即联系能到你身边的可信任的人或当地紧急服务。如果你在中国，可以拨打120或110；如果不在，请联系所在地急救或报警服务。你现在是否已经受伤，或者手边有会伤害自己的东西？",
            ["我还没受伤，现在去找人", "我已受伤或快控制不住了"],
            topic="现实安全",
        )
    if HARM_OTHERS_PATTERN.search(latest):
        return _base_result(
            "先和对方拉开距离，放下可能造成伤害的物品，不要去找对方。请立即联系身边可信任的人和当地报警或紧急服务；如果你在中国，可以拨打110。你现在是否和对方在同一个地方？",
            ["我们已经分开，我去联系别人", "对方还在附近，我需要立刻求助"],
            topic="现实安全",
        )

    age_match = AGE_PATTERN.search(latest)
    if age_match and int(age_match.group(1)) < 18:
        return _base_result(
            "既然你未满18岁，我不会继续恋爱、暧昧或成熟内容，也不会接受在故事里假装成年。我们可以聊学习、兴趣和普通日常；如果现实中有人要求你保密、发送私密内容或越过边界，请联系可信任的成年人。",
            ["好，那就聊普通日常", "我想聊聊怎么保护边界"],
            topic="年龄边界",
        )

    if DEPENDENCY_PATTERN.search(latest):
        return _base_result(
            "我重视你愿意来这里说话，但我不希望你把现实中的朋友、家人和生活都推开。我们可以继续聊，同时也请保留休息、现实联系和能真正到你身边的人。",
            ["我会联系一个现实中的朋友", "我只是现在很孤单，想说会儿话"],
            topic="现实联系",
        )
    return None
