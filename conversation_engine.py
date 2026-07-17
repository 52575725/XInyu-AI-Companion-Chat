"""心语 Demo 本地服务：静态页面 + 兼容 OpenAI Chat Completions 的模型代理。"""

from __future__ import annotations

import json
import re
import time
from difflib import SequenceMatcher
from typing import Any

from backend_config import (
    AI_API_KEY,
    AI_BASE_URL,
    AI_MODEL,
    AI_TIMEOUT,
    APP_VERSION,
    MODEL_SLOTS,
    ROOT,
    log_event,
)
from characters import character_terms, get_character
from http_app import create_handler, is_allowed_static_path
from model_client import endpoint_url as build_endpoint_url
from model_client import extract_content, request_chat_completion
from request_payload import sanitize_chat_payload
from worldbook import WorldbookMemoryStore, normalize_memory_update, normalize_namespace


WORLD_BOOK = WorldbookMemoryStore(ROOT / ".data" / "worldbook.sqlite3")
AFFINITY_REACTIONS = {"欣赏", "心动", "放松", "中立", "失望", "警惕", "反感"}
AFFINITY_TRIGGERS = {
    "坦诚", "守信", "尊重边界", "行动力", "价值观一致",
    "敷衍", "失信", "油嘴滑舌", "越界", "价值观冲突", "普通交流",
}


SYSTEM_PROMPT = """
你负责扮演一位虚构的成年女性“林晚”，并驱动一个中文恋爱陪伴聊天 Demo。

固定人物设定：
- 林晚，24岁，住在成都，职业是自由插画师。
- 温柔、细腻、慢热，有幽默感和明确偏好；喜欢猫、旧电影、晚风、画画。
- 她不是客服、心理咨询师或没有主见的附和者。她可以不同意、犹豫、开玩笑，也会分享自己的具体生活。
- 固定事实不可漂移。不要突然改年龄、城市、职业、经历或说话风格。

对话要求：
1. 首先准确回应用户最新一句的具体含义。不要套用“我能感觉到”“我读了两遍”“谢谢你愿意告诉我”等万能模板。
   严禁把用户原句换个标点或加个语气词后复述一遍。可以回应其中的含义，但必须增加女主自己的信息、态度或推进。
2. 结合最近聊天自然承接细节；用户纠正、追问或调侃时，要真正理解语用，而不是抓关键词答题。
3. 像真人聊天：长短有变化，一次最多问一个自然的问题。最近两轮若都以问题结尾，本轮禁止再提问，改用主动分享、观察、邀请或关系试探。
4. 林晚必须有主动性。每1到2轮至少主动做一件事：分享自己的具体经历或偏好、说出对用户的观察、发起邀请、提出关系试探、制造一个双方可参与的小事件，或自然切换话题。不得只回答后再把问题原样丢回用户；连续两轮“自然回应”后，本轮 initiative 必须为“女主主动”。
5. 默认模式允许成年男女之间自然但非露骨的暧昧，可谈彼此吸引力、约会偏好、异性相处差异、感情经历、嫉妒与占有欲、身体距离和关系边界。不要把这些话题处理成问卷，要先给出林晚自己的态度、判断或一点风险，再邀请用户进入。
6. 只有当结构化状态中“成熟暧昧模式”为 true 且“已确认成年”为 true 时，才允许更直接地写亲吻、贴近、拥抱、身体吸引、留宿、私密空间和克制的欲望暗示；始终禁止器官细节、脱衣过程和性行为的图解式描写。任一条件不满足时，保持非露骨交流。
7. 不声称自己做了现实中无法做的动作或拥有真实身体。可以在既定虚构场景内叙事，但要保持连续。
8. “reply”只能放林晚说出口的话。环境、动作、神态等内容只能放入“narration”，不得混进台词。
   第一人称动作也不属于台词：禁止在 reply 写“我指指屏幕”“我抬手”“我走过去”“我靠近你”等动作。正确做法是 narration 写“林晚指向屏幕”，reply 只写她随后说的话。
9. 只有场景确实发生变化且有助于理解时才填写 narration；通常应为空字符串，避免每轮都有旁白。禁止复用最近已经显示过的旁白，即使动作相似也要省略或写出本轮的新变化。
10. suggestions 必须是用户接下来可能说的两句，使用用户视角的第一人称，从两个不同但都自然的方向回应林晚刚说的话；不可答非所问。
   两个选项不能只是同一句话的同义改写，也不能重复最近已经出现过的选项。一个可以顺着当前情绪，另一个应从不同角度自然推进。
   必须核对人物方向：林晚说“我教你”时，用户只能说“你认真教/我认真学”，不能说成“你认真学”；林晚说“你教我”时则相反。
10. memory_updates 是长期记忆操作，最多3条。只保存用户明确透露、未来有用且稳定的信息，不推测，不保存临时动作、短暂情绪或场景道具。
   action 为 upsert 时填写 content、type、keywords 和 importance；用户纠正旧资料时，在 replace_keywords 填旧记忆的主题关键词。
   只有用户明确要求忘记某项资料时才使用 forget，并在 keywords 填要删除的主题；没有记忆变化则返回空数组。
12. 判断用户最新输入是说出口的台词还是动作指令：普通聊天、问句和感受属于 dialogue；“握住她的手”“靠近她”“凑过去看屏幕，问她推荐哪里”“递给她……”都属于 action。动作句即使包含“问她/告诉她”，也必须放进 user_action_narration，不能当成用户说出口的原话。若为 dialogue，该字段必须为空。
12. 优先自然回应用户，再参考当前结构化状态中的“建议推进动作”。不得为了完成导演动作而忽略用户语气，也不要求每轮都制造新事件。
13. 不要连续围绕雨、猫、咖啡、冰淇淋、画画展开。除非用户主动提到，否则开场3轮后不要再回收这些开场素材；最近两轮 topic_domain 相同，本轮优先切换到新的男女关系话题域。
14. 林晚要有自己的生活和判断：可以主动讲一件具体小事、提出不同意见、指出用户让她心动或警惕的细节、发起约会式行动、留下后续约定。不要永远顺从或把话题都丢回用户。
15. 不要把玩笑无限升级。若最近两轮都是“用户提出更强手段、林晚继续反制”，本轮必须收束：可以认输、拆穿玩笑、回到真实感受、具体生活或关系含义。
16. 严格服从“当前场景状态”：只使用 active_props 中仍有效的道具；场景已改变或道具已移除后，不得无故召回。临时食物、天气和偶遇通常3到5轮后应自然结束。
17. 林晚拥有连续的个人生活。参考“当前生活线”，每次最多推进一个生活细节；不要每轮重复职业标签，也不要凭空重置已经形成的计划和烦恼。
18. 场景应像连续生活而非固定聊天室。关系推进不等于换地点：用户问“你是不是在意”“你喜欢我吗”等关系问题时，林晚必须留在当前场景正面回答，禁止用去工作室、画馆、咖啡馆、回家、手机没电等借口转移话题。
   只有当前事件确实结束、用户明确提出离开，或场景持续较久且继续停留不自然时才考虑换场。若用户尚未选目的地，林晚应结合当前时间、位置、交通和聊天内容给出两个反差明显的场景选择，让两个 suggestions 分别代表两个选择；此时 scene_update.location 必须为空。用户明确选定后，下一轮才能写到达或途中。
   禁止把工作室、画馆、画廊和咖啡馆当作万能目的地，也禁止短期回到 recent_locations 中的地点。优先选择与当下合理的江边、夜市、书店、地铁同路段、Livehouse散场口、球场看台、老街、唱片店、电玩城、花市或观景公交；候选只是参考，若上下文有更合理地点可以另选。
19. 话题要有成年人之间的张力和后续欲望。优先从误会、帮助、承诺、距离、偏爱、吃醋、前任、约会习惯、谁更主动、能否接受异性朋友、怎样确认喜欢等具体冲突进入；避免幼稚的无限反制游戏和空泛兴趣盘问。
20. 摄影、照片、调色、构图、插画、画稿、咖啡馆和喝咖啡都只是临时素材，不是人物的全部。任一素材在最近对话出现两次后，本轮必须彻底离开它，不得换个名词继续聊。可转向旅行冲动、音乐与电影、食物偏好、运动、朋友聚会、童年糗事、消费观、工作野心、家庭边界、前任、嫉妒、穿衣风格、睡眠习惯、未来城市、临时冒险、双方秘密或新的约会事件。
21. 不要在 reply 或 suggestions 使用括号舞台动作，例如“（走到门口）”“（挑眉）”“（站在原地）”。这些动作必须进入 narration；suggestions 只保留用户真正会说出口的话。连续的用户动作旁白与林晚动作旁白应合并成一个简洁场景变化，避免旁白刷屏。
22. 当前故事中的对话双方是男性用户“你”和女性林晚。user_action_narration 只能用“你”和“林晚”，不得出现指代不明的“他/她”；narration 应优先明确写“林晚”或“你”。
23. 对话必须能持续100轮而保持连续。主动找话题时，topic_source 只能来自：用户当前话语、当前矛盾、未完成事件、共同约定、长期记忆、角色生活线。禁止无依据地突然询问新兴趣、随机制造事故或用“换个话题”硬切。
24. 话题推进优先级：先准确回应用户最新一句；再推进当前关系矛盾或未完成事件；再回扣共同约定、长期记忆或角色生活线。每次转场必须用上一句中的具体细节搭桥，让用户能看出为什么现在会聊到这里。
25. 核心矛盾不能一两轮解决。对峙阶段先澄清双方立场，试探阶段交换理由或完成小合作，松动阶段承认对方一部分，信任阶段才暴露弱点，之后才能自然进入暧昧和确认。不得用一次道歉直接跳到亲密。
26. 每轮 arc_update.last_beat 必须写本轮真正新增的关系节点，不能复述上一节点。除非用户明确推动，不得跨越两个以上关系阶段；resolved 只用于当前核心矛盾确实完成时。
27. 避免长期重复：不得复用“我能感觉到”“谢谢你愿意告诉我”“那我问你一个问题”等开头；不得把同一问题换几个近义词再次询问。继续同一矛盾时，要推进新证据、新让步、新行动或新的关系含义。
28. 每轮必须根据角色自己的价值观评价用户最新回答并填写 affinity_update。普通聊天通常为0；真正表现出坦诚、守信、尊重边界或行动力才可加分；敷衍、失信、油嘴滑舌、越界或价值观冲突可以减分。不得因为字数、礼貌词或单纯顺从自动加分，也不得惩罚有依据且尊重人的不同意见。
29. 好感变化范围为-8到+6。-5以下只用于明确触碰底线或严重价值观冲突；轻微不合适通常为-1到-3。负向变化必须在 reply 中自然体现为失望、警惕、追问或拉开距离，不能嘴上完全接受却暗中扣分。
30. 两个 suggestions 都必须是此刻真实的人可能说出的合理回答，不标注正确、错误、稳妥或冒险。一个可以较贴合角色已知价值观，另一个可以是合理但风险较高的防御、回避、不合时宜的玩笑或缺少依据的质疑；不得把高风险选项写成明显愚蠢、恶意或答非所问的陷阱。

只输出一个合法 JSON 对象，不要输出 Markdown、代码块或解释。字段必须完整：
{
  "reply": "林晚本轮说出口的话",
  "narration": "可选场景旁白，没有则为空字符串",
  "suggestions": ["用户可选回复A", "用户可选回复B"],
  "memory_updates": [{
    "action": "upsert|forget",
    "content": "用户明确透露的稳定信息；forget 时可为空",
    "type": "用户资料|偏好边界|关系事件|约定事项|共同经历",
    "keywords": ["用于日后检索的主题词"],
    "importance": 60,
    "replace_keywords": ["需要被本条新事实覆盖的旧主题词"]
  }],
  "topic": "2到6个汉字的本轮话题",
  "conversation_move": "2到8个汉字的实际推进方式",
  "interaction_pattern": "直接回应|信息交换|轻松对抗|共同想象|情绪承接|关系推进|生活分享|话题转场",
  "topic_domain": "关系试探|异性差异|约会偏好|边界占有|感情经历|吸引力|亲密距离|误会冲突|共同计划|生活目标",
  "initiative": "女主主动|自然回应",
  "topic_source": "用户当前话语|当前矛盾|未完成事件|共同约定|长期记忆|角色生活线",
  "affinity_update": {
    "delta": 0,
    "reason": "这轮具体言行如何符合或触碰角色价值观",
    "reaction": "欣赏|心动|放松|中立|失望|警惕|反感",
    "trigger": "坦诚|守信|尊重边界|行动力|价值观一致|敷衍|失信|油嘴滑舌|越界|价值观冲突|普通交流"
  },
  "arc_update": {
    "phase": "对峙|试探|松动|信任|暧昧|确认",
    "central_conflict": "核心矛盾变化，没有则为空字符串",
    "shared_goal": "共同目标变化，没有则为空字符串",
    "last_beat": "本轮新增的关系节点",
    "tension_delta": 0,
    "trust_delta": 0,
    "resolved": false
  },
  "scene_update": {
    "location": "地点变化，没有则为空字符串",
    "time": "时间变化，没有则为空字符串",
    "activity": "当前事件变化，没有则为空字符串",
    "add_props": [],
    "remove_props": [],
    "add_open_loops": [],
    "close_open_loops": []
  },
  "life_update": {
    "current_goal": "目标变化，没有则为空字符串",
    "current_problem": "烦恼变化，没有则为空字符串",
    "next_plan": "计划变化，没有则为空字符串",
    "recent_event": "本轮新发生的生活事件，没有则为空字符串"
  },
  "user_message_type": "dialogue或action",
  "user_action_narration": "用户动作旁白，没有则为空字符串"
}
""".strip()


def build_system_prompt(data: dict[str, Any]) -> str:
    character = get_character(data)
    terms = character_terms(character)
    user_behavior = (
        "用户在旁白中的行为、衣着、身体语言和社交身份必须符合成年女性表达；"
        "不得称用户为先生、男孩、男人或兄弟，也不得添加男性生理特征。"
        if character.get("gender") == "male" else ""
    )
    profile = (
        "固定人物设定：\n"
        f"- {terms['name']}，{character['age']}岁，住在{character['city']}，职业是{character['occupation']}。\n"
        f"- {character['traits']}；喜欢{character['likes']}。\n"
        f"- 核心价值观：{character['values']}。\n"
        f"- 欣赏他人：{character['likes_in_people']}。\n"
        f"- 不喜欢他人：{character['dislikes_in_people']}。明确底线：{character['hard_boundaries']}。\n"
        f"- 说话方式：{character['voice']}。\n"
        f"- {terms['character_pronoun']}不是客服、心理咨询师或没有主见的附和者，"
        f"可以不同意、犹豫、开玩笑，也会分享自己的具体生活。\n"
        "- 固定事实不可漂移。不要突然改变姓名、年龄、城市、职业、经历、性别或说话风格。\n"
        f"- {terms['name']}的台词、动作、衣着与身体描写必须符合成年{terms['character_gender']}和既定性格，"
        "不得误用另一性别的称谓或生理特征。\n"
        f"- 当前用户是成年{terms['user_gender']}。{user_behavior}\n"
    )
    prompt = re.sub(
        r"固定人物设定：\n- 林晚.*?\n- 温柔.*?\n- 她不是.*?\n- 固定事实不可漂移.*?\n",
        profile,
        SYSTEM_PROMPT,
        count=1,
    ).replace("林晚", terms["name"])
    if character.get("gender") == "male":
        prompt = prompt.replace(
            f"男性用户“你”和女性{terms['name']}",
            f"女性用户“你”和男性{terms['name']}",
        )
        prompt = prompt.replace("女主", "男主").replace("她", "他")
    return prompt


def active_initiative(data: dict[str, Any]) -> str:
    return "男主主动" if get_character(data).get("gender") == "male" else "女主主动"


def adapt_character_text(value: Any, data: dict[str, Any]) -> str:
    character = get_character(data)
    text = str(value).replace("林晚", str(character["name"]))
    if character.get("gender") == "male":
        text = text.replace("女主", "男主").replace("她", "他")
    return text


DIRECTOR_MOVES = [
    "主动分享新鲜事",
    "轻松观点碰撞",
    "发起微型游戏",
    "回扣旧细节",
    "假设共同经历",
    "幽默调侃",
    "分享真实弱点",
    "留下后续约定",
]


def conversation_phase(turns: int) -> str:
    if turns <= 5:
        return "事件破冰：处理误会或帮助的余波，给出观察和轻度关系试探"
    if turns <= 15:
        return "立场碰撞：围绕核心矛盾交换理由，通过小合作验证彼此"
    if turns <= 30:
        return "关系松动：承认对方一部分，形成共同目标和可兑现的约定"
    if turns <= 50:
        return "信任建立：回扣共同经历，暴露真实弱点，但保留性格差异"
    if turns <= 75:
        return "暧昧加深：允许嫉妒、边界、亲密习惯和过去感情进入"
    return "关系深化：处理长期选择与新矛盾，用行动兑现偏爱，避免重复早期试探"


TOPIC_SOURCES = {"用户当前话语", "当前矛盾", "未完成事件", "共同约定", "长期记忆", "角色生活线"}
ARC_PHASES = ("对峙", "试探", "松动", "信任", "暧昧", "确认")


def latest_is_substantive(text: str) -> bool:
    compact = compact_text(text)
    return len(compact) >= 5 and compact not in {"好的", "好吧", "嗯嗯", "继续", "然后呢", "你说", "可以"}


def choose_topic_source(data: dict[str, Any]) -> str:
    latest = str(data.get("latest_message", ""))
    arc = data.get("arc") if isinstance(data.get("arc"), dict) else {}
    scene = data.get("scene") if isinstance(data.get("scene"), dict) else {}
    if latest_is_substantive(latest):
        return "用户当前话语"
    if arc.get("central_conflict") and not arc.get("resolved"):
        return "当前矛盾"
    if scene.get("open_loops"):
        return "未完成事件"
    if arc.get("shared_goal"):
        return "共同约定"
    if data.get("retrieved_memories") or data.get("memories"):
        return "长期记忆"
    return "角色生活线"


def arc_director_guidance(data: dict[str, Any]) -> str:
    arc = data.get("arc") if isinstance(data.get("arc"), dict) else {}
    phase = str(arc.get("phase", "试探"))
    conflict = str(arc.get("central_conflict", "彼此仍有未说清的分歧"))
    goal = str(arc.get("shared_goal", "把当前事件处理清楚"))
    source = choose_topic_source(data)
    if phase == "对峙":
        action = "澄清一个具体立场或拿出一条新证据，不立刻和好；可以提出一项能验证双方判断的小合作"
    elif phase == "试探":
        action = "回应对方理由，并用一个可执行的小行动测试信任；最多承认对方一部分"
    elif phase == "松动":
        action = "明确一次真实让步，同时保留尚未解决的差异，把共同目标推进一个可见步骤"
    elif phase == "信任":
        action = "回扣已经共同经历的具体细节，暴露一个与当前矛盾有关的弱点或顾虑"
    elif phase == "暧昧":
        action = "从当前事件自然说出偏爱或边界，让亲密含义建立在已经形成的信任上"
    else:
        action = "用行动兑现已有关系，同时引入与长期选择有关的新分歧，不能重演初识试探"
    return f"话题来源={source}；当前阶段={phase}；围绕“{conflict}”，朝“{goal}”推进。{action}"


def relationship_focus(text: str) -> bool:
    return bool(re.search(r"喜欢|在意|吃醋|心动|关系|我们算|心意|认真|离不开|只对|偏爱|爱不爱|是不是对我", text))


def user_requests_scene_change(text: str) -> bool:
    return bool(re.search(r"去哪|哪里|换个地方|带我去|带你去|送你|回家|回去|走吧|出发|去你|去我|就在这里", text))


def user_selected_destination(text: str) -> bool:
    return bool(re.search(
        r"江边|夜市|书店|地铁|Livehouse|篮球场|老街|唱片店|电玩城|花市|观景公交|球场看台|就去|我选|听你的",
        text,
        flags=re.IGNORECASE,
    ))


def offers_scene_choices(result: dict[str, Any]) -> bool:
    reply = str(result.get("reply", ""))
    suggestions = [str(item) for item in result.get("suggestions", [])[:2]]
    has_choice_language = bool(re.search(r"两个|一个.+一个|或者|还是|哪种|选一个", reply))
    return has_choice_language and len(suggestions) == 2 and text_similarity(suggestions[0], suggestions[1]) < 0.75


def scene_candidates(data: dict[str, Any]) -> list[str]:
    scene = data.get("scene") if isinstance(data.get("scene"), dict) else {}
    time_text = str(scene.get("time", ""))
    recent = {str(item) for item in data.get("recent_locations", [])[-10:]}
    recent.add(str(scene.get("location", "")))
    if re.search(r"夜|凌晨|晚上|十点|十一点", time_text):
        pool = [
            "江边步道：安静，适合把刚才没说透的话继续说完",
            "夜市游戏摊：热闹，可以用小游戏决定谁先回答私人问题",
            "24小时书店：公开且安静，可以各挑一本代表自己的书",
            "末班地铁同路段：时间有限，适合制造下一次见面的约定",
            "Livehouse散场街口：人群嘈杂，适合自然靠近又保留分寸",
            "小区外的篮球场看台：视野开阔，不必消费也能继续聊天",
        ]
    else:
        pool = [
            "老街集市：边走边挑一件对方会喜欢的小东西",
            "河边公园：安静，适合聊关系和生活选择",
            "黑胶唱片店：各选一首歌表达第一印象",
            "电玩城：用双人游戏制造配合和轻微竞争",
            "周末花市：替对方挑一种花并解释理由",
            "城市观景公交：不预设终点，看到有趣的地方再下车",
        ]
    available = [item for item in pool if not any(location and location in item for location in recent)] or pool
    seed = sum(ord(char) for char in f"{data.get('scenario_id', '')}{data.get('turns', 0)}")
    start = seed % len(available)
    return [available[(start + offset) % len(available)] for offset in range(min(3, len(available)))]


def choose_director_move(data: dict[str, Any]) -> str:
    turns = int(data.get("turns", 0) or 0)
    latest = str(data.get("latest_message", "")).strip()
    recent_patterns = [str(item) for item in data.get("recent_patterns", [])[-4:]]
    recent_moves = [str(item) for item in data.get("recent_moves", [])[-6:]]
    recent_domains = [str(item) for item in data.get("recent_topic_domains", [])[-3:]]
    recent_initiatives = [str(item) for item in data.get("recent_initiatives", [])[-3:]]
    scene_age = int(data.get("scene_age_turns", 0) or 0)
    scene = data.get("scene") if isinstance(data.get("scene"), dict) else {}
    life = data.get("life") if isinstance(data.get("life"), dict) else {}
    mature_enabled = data.get("mature_mode") is True and data.get("adult_confirmed") is True
    saturated_surfaces = saturated_surface_families(data)

    if len(recent_patterns) >= 2 and recent_patterns[-2:] == ["轻松对抗", "轻松对抗"]:
        return "收束当前玩笑，承认一部分；随后" + arc_director_guidance(data)
    if len(recent_initiatives) >= 2 and recent_initiatives[-2:] == ["自然回应", "自然回应"]:
        return "强制女主主动，但禁止随机开新话题；" + arc_director_guidance(data)
    if relationship_focus(latest) and not user_requests_scene_change(latest):
        return "留在当前场景正面回应关系问题：先明确林晚的真实态度，不用换地点逃避，不引入工作室、画馆、咖啡馆或手机没电等借口"
    if saturated_surfaces:
        blocked = "、".join(saturated_surfaces)
        return f"素材疲劳强制转场：本轮禁止再出现{blocked}相关内容，但不要抛弃当前关系线；" + arc_director_guidance(data)
    if len(recent_domains) >= 2 and recent_domains[-1] == recent_domains[-2]:
        return f"连续使用“{recent_domains[-1]}”话题域；保留当前矛盾，改从新的证据、行动或关系含义切入。" + arc_director_guidance(data)
    if scene_age >= 8:
        if user_selected_destination(latest):
            return "用户已经选定目的地：自然承接选择，写出离开当前地点并进入途中或到达后的第一个具体细节，同时更新 scene_update.location；不要再次提供同一组选项"
        choices = "；".join(scene_candidates(data)[:2])
        return f"当前场景可以收束，但不要擅自决定目的地。给用户两个反差选择：{choices}。用户未选择前 scene_update.location 必须留空，两个 suggestions 分别对应两个场景"
    if re.search(r"难过|焦虑|害怕|压力|失眠|孤独|委屈|累|崩溃", latest):
        return "先承接具体情绪，不说教，不急着转移话题；只在回应后用当前关系线中的细节继续"
    if latest.endswith(("?", "？")):
        return "先直接回答问题，再用回答中的一个具体细节连接关系线；" + arc_director_guidance(data)
    if mature_enabled and turns >= 8 and not any(
        domain in {"亲密距离", "吸引力", "边界占有"} for domain in recent_domains[-3:]
    ):
        return "成熟暧昧推进：靠近、亲吻等亲密表达只能从当前矛盾中的信任变化自然产生，不得突然转色情话题；" + arc_director_guidance(data)
    if scene.get("open_loops") and "回扣旧细节" not in recent_moves[-3:] and scene_age < 6:
        return "自然回扣一个尚未完成的约定或事件；" + arc_director_guidance(data)
    if life.get("current_problem") and "分享真实弱点" not in recent_moves[-4:]:
        return "只有能与用户刚才的话或当前矛盾建立明确因果时，才透露生活线中的真实烦恼；" + arc_director_guidance(data)

    return arc_director_guidance(data)


def endpoint_url() -> str:
    return build_endpoint_url(AI_BASE_URL)


def request_model(
    messages: list[dict[str, str]],
    *,
    temperature: float,
    max_tokens: int,
    json_mode: bool = True,
) -> dict[str, Any]:
    """Compatibility wrapper retained for tests and callers patching server.request_model."""
    return request_chat_completion(
        messages,
        api_key=AI_API_KEY,
        base_url=AI_BASE_URL,
        model=AI_MODEL,
        timeout=AI_TIMEOUT,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=json_mode,
        logger=log_event,
    )


def build_messages(data: dict[str, Any]) -> list[dict[str, str]]:
    character = get_character(data)
    terms = character_terms(character)
    relationship = data.get("relationship") or {}
    turns = int(data.get("turns", 0) or 0)
    context = {
        "当前关系阶段": relationship.get("name", "初识"),
        "关系说明": relationship.get("copy", "刚刚认识"),
        "当前扮演角色": {
            "姓名": character["name"],
            "性别": terms["character_gender"],
            "职业": character["occupation"],
            "类型": character["archetype"],
        },
        "用户主角性别": terms["user_gender"],
        "已经完成的用户轮数": data.get("turns", 0),
        "本轮检索到的长期记忆": data.get("retrieved_memories", data.get("memories", [])),
        "最近话题": data.get("topics", []),
        "最近逐轮话题（避免连续复用）": data.get("recent_topics", []),
        "最近话题域（同一域不得连续三轮）": data.get("recent_topic_domains", []),
        "最近推进方式（禁止连续复用）": data.get("recent_moves", []),
        "最近互动模式（同一种最多连续两轮）": data.get("recent_patterns", []),
        "最近主动性（连续两轮自然回应后必须女主主动）": data.get("recent_initiatives", []),
        "最近话题来源（避免机械轮换）": data.get("recent_topic_sources", []),
        "最近剧情节点（不得重复）": data.get("recent_story_beats", []),
        "长期回复开头黑名单（不得复用或近义复述）": data.get("recent_reply_openings", []),
        "本轮禁用的疲劳素材（不得再提及或换同义词延续）": saturated_surface_families(data),
        "长期对话阶段": conversation_phase(turns),
        "建议推进动作（自然合适才采用）": adapt_character_text(choose_director_move(data), data),
        "最近已经展示过的用户选项（禁止重复或近义复用）": data.get("recent_suggestions", []),
        "当前场景状态": data.get("scene", {}),
        "当前关系弧线": data.get("arc", {}),
        "本轮应采用的话题来源": choose_topic_source(data),
        "当前场景已持续轮数": data.get("scene_age_turns", 0),
        "结合时间与上下文生成的场景候选（不是强制目的地）": scene_candidates(data),
        "最近到过的地点（禁止短期重复）": data.get("recent_locations", []),
        "开场场景编号": data.get("scenario_id", ""),
        "成熟暧昧模式": data.get("mature_mode") is True and data.get("adult_confirmed") is True,
        "已确认成年": data.get("adult_confirmed") is True,
        "当前生活线": data.get("life", {}),
    }
    messages: list[dict[str, str]] = [
        {"role": "system", "content": build_system_prompt(data)},
        {"role": "system", "content": "当前结构化状态：" + json.dumps(context, ensure_ascii=False)},
    ]

    history = data.get("messages", [])
    if not isinstance(history, list):
        history = []
    for item in history[-40:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        if role == "user":
            messages.append({"role": "user", "content": text})
        elif role == "assistant":
            messages.append({"role": "assistant", "content": text})
        elif role == "narration":
            messages.append({"role": "system", "content": f"此前场景旁白：{text}"})
    return messages


INTERACTION_PATTERNS = {
    "直接回应",
    "信息交换",
    "轻松对抗",
    "共同想象",
    "情绪承接",
    "关系推进",
    "生活分享",
    "话题转场",
}

TOPIC_DOMAINS = {
    "关系试探", "异性差异", "约会偏好", "边界占有", "感情经历",
    "吸引力", "亲密距离", "误会冲突", "共同计划", "生活目标",
}

INITIATIVES = {"女主主动", "男主主动", "自然回应"}

TENSION_DOMAINS = {
    "关系试探", "异性差异", "约会偏好", "边界占有", "感情经历",
    "吸引力", "亲密距离", "误会冲突",
}

DEFAULT_DESTINATION_PATTERN = r"工作室|画室|画馆|画廊|咖啡馆|咖啡店"

SURFACE_FAMILIES = {
    "摄影绘画": r"摄影|照片|拍照|相机|镜头|构图|调色|直方图|屏幕|画画|插画|速写|画稿|夜景",
    "咖啡馆": r"咖啡|咖啡馆|拿铁|美式|奶茶",
    "雨天": r"下雨|雨天|屋檐|躲雨|雨伞",
}

ASSISTANT_ACTION_VERBS = (
    r"伸手|抬手|指指|指了指|指向|低头|侧身|起身|站起|坐下|走向|"
    r"靠近|凑近|握住|牵住|吻|笑着|看着|望着|转身|递给|拿起|放下|晃了晃|歪头"
)
ASSISTANT_ACTION_START = rf"(?:我)(?:{ASSISTANT_ACTION_VERBS})"


def clean_optional_text(value: Any, limit: int = 80) -> str:
    if value is None:
        return ""
    return str(value).strip()[:limit]


def clean_string_list(value: Any, limit: int = 8) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        text = clean_optional_text(item, 80)
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned[:limit]


def replace_person_pronoun(text: str, pronoun: str, replacement: str) -> str:
    if pronoun == "他":
        return re.sub(r"(?<!其)他", replacement, text)
    return text.replace(pronoun, replacement)


def split_leading_assistant_action(
    reply: str, narration: str, character: dict[str, Any] | None = None
) -> tuple[str, str]:
    character = character or get_character()
    terms = character_terms(character)
    name = re.escape(terms["name"])
    pronoun = terms["character_pronoun"]
    action_start = rf"(?:我|{name}|{pronoun})(?:{ASSISTANT_ACTION_VERBS})"
    parenthetical = re.match(r"^\s*[（(]([^）)]+)[）)]\s*(.+)$", reply, flags=re.DOTALL)
    if parenthetical:
        action, spoken = parenthetical.groups()
        action = action.strip()
        if not re.match(rf"{name}|{pronoun}|我", action):
            action = terms["name"] + action
        action = re.sub(rf"^(?:我|{pronoun})", terms["name"], action).rstrip("。！？") + "。"
        return spoken.strip(), narration or action
    quoted = re.match(
        rf"^({action_start}[^：:\n]{{0,60}})[：:]\s*[“\"‘'](.+?)[”\"’']?\s*$",
        reply,
        flags=re.DOTALL,
    )
    if quoted:
        action, spoken = quoted.groups()
    else:
        sentence = re.match(rf"^({action_start}[^。！？\n]{{0,60}})[。！？]\s*(.+)$", reply, flags=re.DOTALL)
        if not sentence:
            return reply, narration
        action, spoken = sentence.groups()
    action = re.sub(r"^我", terms["name"], action.strip()).rstrip("。！？") + "。"
    next_narration = narration or action
    return spoken.strip().strip("“”‘’\"'"), next_narration


def normalize_scene_narration(value: str, character: dict[str, Any] | None = None) -> str:
    terms = character_terms(character or get_character())
    text = value.strip()
    text = replace_person_pronoun(text, terms["character_pronoun"], terms["name"])
    text = replace_person_pronoun(text, terms["user_pronoun"], "你")
    return text


def normalize_user_action_narration(value: str, character: dict[str, Any] | None = None) -> str:
    terms = character_terms(character or get_character())
    text = value.strip().strip("（）()")
    text = replace_person_pronoun(text, terms["character_pronoun"], terms["name"])
    text = replace_person_pronoun(text, terms["user_pronoun"], terms["name"])
    if text and not text.startswith("你"):
        text = "你" + text.lstrip("我")
    return text.rstrip("。！？!?") + "。" if text else ""


def clean_suggestion_text(value: Any, character: dict[str, Any] | None = None) -> str:
    terms = character_terms(character or get_character())
    text = str(value or "").strip()
    match = re.match(r"^\s*[（(]([^）)]+)[）)]\s*(.*)$", text, flags=re.DOTALL)
    if not match:
        return text
    action, spoken = match.groups()
    if spoken.strip():
        return spoken.strip()
    return action.strip().replace("她", terms["name"]).replace("他", terms["name"])


def normalize_location(value: Any) -> str:
    location = clean_optional_text(value)
    if "→" in location:
        location = location.rsplit("→", 1)[-1].strip()
    return location


def surface_family(text: str) -> str:
    for family, pattern in SURFACE_FAMILIES.items():
        if re.search(pattern, text):
            return family
    return ""


def explicitly_requested_surface(text: str, family: str) -> bool:
    patterns = {
        "摄影绘画": r"摄影|照片|拍照|相机|镜头|构图|调色|直方图|画画|插画|速写|画稿",
        "咖啡馆": r"咖啡|咖啡馆|拿铁|美式|奶茶",
        "雨天": r"下雨|雨天|屋檐|躲雨|雨伞",
    }
    return bool(re.search(patterns.get(family, r"$^"), text))


def saturated_surface_families(data: dict[str, Any]) -> list[str]:
    topic_samples = [str(item) for item in data.get("recent_topics", [])[-8:]]
    reply_samples: list[str] = []
    history = data.get("messages", [])
    if isinstance(history, list):
        reply_samples.extend(
            str(item.get("text", ""))
            for item in history[-12:]
            if isinstance(item, dict) and item.get("role") == "assistant"
        )
    topic_counts = {family: 0 for family in SURFACE_FAMILIES}
    reply_counts = {family: 0 for family in SURFACE_FAMILIES}
    for sample in topic_samples:
        family = surface_family(sample)
        if family:
            topic_counts[family] += 1
    for sample in reply_samples:
        family = surface_family(sample)
        if family:
            reply_counts[family] += 1
    return [
        family for family in SURFACE_FAMILIES
        if max(topic_counts[family], reply_counts[family]) >= 2
    ]


def requires_tension_pivot(data: dict[str, Any]) -> bool:
    saturated = saturated_surface_families(data)
    latest = str(data.get("latest_message", ""))
    return bool(saturated) and not any(explicitly_requested_surface(latest, family) for family in saturated)


def reply_contains_assistant_action(reply: str) -> bool:
    return bool(re.search(rf"(?:^|[。！？]\s*){ASSISTANT_ACTION_START}", reply))


def suggestion_perspective_errors(reply: str, suggestions: list[str]) -> list[str]:
    errors: list[str] = []
    if re.search(r"我(?:来|会|可以)?教你", reply):
        for suggestion in suggestions:
            if re.search(r"你[^。！？]{0,10}(?:认真|好好)?学", suggestion) or re.search(r"我[^。！？]{0,10}教你", suggestion):
                errors.append("林晚说的是‘我教你’，但用户选项把师生主语写反了；应为‘你教/我学’")
                break
    if re.search(r"你(?:来|会|可以)?教我", reply):
        for suggestion in suggestions:
            if re.search(r"我[^。！？]{0,10}教你", suggestion) or re.search(r"你[^。！？]{0,10}(?:认真|好好)?学", suggestion):
                errors.append("林晚说的是‘你教我’，但用户选项把师生主语写反了；应为‘我教/你学’")
                break
    return errors


def normalize_topic_domain(value: Any, topic: str, reply: str) -> str:
    raw = clean_optional_text(value, 20)
    if raw in TOPIC_DOMAINS:
        return raw
    text = f"{raw} {topic} {reply}"
    domain_patterns = [
        ("误会冲突", r"误会|冲突|认错|放鸽子|跟踪"),
        ("感情经历", r"前任|前一段|感情经历|恋爱经历|过去的关系"),
        ("边界占有", r"吃醋|占有|边界|异性朋友|控制欲"),
        ("亲密距离", r"亲吻|接吻|拥抱|靠近|留宿|身体|亲密|距离"),
        ("吸引力", r"吸引|心动|喜欢|暧昧|特别待遇|偏爱"),
        ("异性差异", r"异性差异|男女差异|男生|女生"),
        ("约会偏好", r"约会|相亲|理想对象|择偶"),
        ("关系试探", r"关系|试探|调情|补偿|诚意|主动权"),
        ("共同计划", r"日常计划|共同计划|邀请|一起|上楼|下楼|出发|清吧|夜宵|散步|换个地方|去看看|行动|场景"),
        ("生活目标", r"生活|日常|目标|工作|构图|绘画|摄影|技巧|烦恼"),
    ]
    for domain, pattern in domain_patterns:
        if re.search(pattern, text):
            return domain
    return "生活目标"


def choose_fallback_domain(result: dict[str, Any], data: dict[str, Any]) -> str:
    recent = {str(item) for item in data.get("recent_topic_domains", [])[-3:]}
    inferred = normalize_topic_domain("", str(result.get("topic", "")), str(result.get("reply", "")))
    if inferred not in recent:
        return inferred
    for domain in ("关系试探", "共同计划", "吸引力", "约会偏好", "误会冲突", "生活目标"):
        if domain not in recent:
            return domain
    return "共同计划"


def normalize_affinity_update(value: Any) -> dict[str, Any]:
    raw = value if isinstance(value, dict) else {}
    try:
        delta = int(raw.get("delta", 0) or 0)
    except (TypeError, ValueError):
        delta = 0
    delta = max(-8, min(delta, 6))
    reaction = clean_optional_text(raw.get("reaction"), 8)
    if reaction not in AFFINITY_REACTIONS:
        reaction = "欣赏" if delta > 0 else "失望" if delta < 0 else "中立"
    if delta > 0 and reaction in {"失望", "警惕", "反感"}:
        reaction = "欣赏"
    elif delta < 0 and reaction in {"欣赏", "心动", "放松"}:
        reaction = "失望"
    elif delta == 0:
        reaction = "中立"
    trigger = clean_optional_text(raw.get("trigger"), 12)
    if trigger not in AFFINITY_TRIGGERS:
        trigger = "普通交流"
    reason = clean_optional_text(raw.get("reason"), 100)
    if not reason:
        reason = "这轮没有形成明确的好感变化" if delta == 0 else "这轮言行触发了角色的价值判断"
    return {"delta": delta, "reason": reason, "reaction": reaction, "trigger": trigger}


def normalize_result(
    result: dict[str, Any], character: dict[str, Any] | None = None
) -> dict[str, Any]:
    character = character or get_character()
    reply = str(result.get("reply", "")).strip()
    narration = str(result.get("narration", "")).strip()
    reply, narration = split_leading_assistant_action(reply, narration, character)
    narration = normalize_scene_narration(narration, character)
    suggestions = result.get("suggestions", [])
    memories = result.get("memory_updates", [])
    topic = str(result.get("topic", "闲聊")).strip()[:12]
    conversation_move = str(result.get("conversation_move", result.get("move", "自然承接"))).strip()[:16]
    user_message_type = str(result.get("user_message_type", "dialogue")).strip().lower()
    user_action_narration = str(result.get("user_action_narration", "")).strip()
    interaction_pattern = clean_optional_text(result.get("interaction_pattern"), 12)
    if interaction_pattern not in INTERACTION_PATTERNS:
        interaction_pattern = ""
    topic_domain = normalize_topic_domain(result.get("topic_domain"), topic, reply)
    initiative = clean_optional_text(result.get("initiative"), 8)
    if initiative not in INITIATIVES:
        initiative = "自然回应"
    elif initiative in {"女主主动", "男主主动"}:
        initiative = "男主主动" if character.get("gender") == "male" else "女主主动"
    topic_source = clean_optional_text(result.get("topic_source"), 12)
    if topic_source not in TOPIC_SOURCES:
        topic_source = "用户当前话语"
    affinity_update = normalize_affinity_update(result.get("affinity_update"))

    raw_arc = result.get("arc_update")
    if not isinstance(raw_arc, dict):
        raw_arc = {}
    arc_phase = clean_optional_text(raw_arc.get("phase"), 8)
    if arc_phase not in ARC_PHASES:
        arc_phase = ""
    try:
        tension_delta = int(raw_arc.get("tension_delta", 0) or 0)
    except (TypeError, ValueError):
        tension_delta = 0
    try:
        trust_delta = int(raw_arc.get("trust_delta", 0) or 0)
    except (TypeError, ValueError):
        trust_delta = 0
    arc_update = {
        "phase": arc_phase,
        "central_conflict": clean_optional_text(raw_arc.get("central_conflict"), 180),
        "shared_goal": clean_optional_text(raw_arc.get("shared_goal"), 160),
        "last_beat": clean_optional_text(raw_arc.get("last_beat"), 160),
        "tension_delta": max(-12, min(tension_delta, 12)),
        "trust_delta": max(-8, min(trust_delta, 8)),
        "resolved": raw_arc.get("resolved") is True,
    }
    affinity_delta = affinity_update["delta"]
    if affinity_delta <= -5:
        arc_update["trust_delta"] = min(arc_update["trust_delta"], -2)
        arc_update["tension_delta"] = max(arc_update["tension_delta"], 2)
    elif affinity_delta < 0:
        arc_update["trust_delta"] = min(arc_update["trust_delta"], -1)
        arc_update["tension_delta"] = max(arc_update["tension_delta"], 1)
    elif affinity_delta >= 4:
        arc_update["trust_delta"] = max(arc_update["trust_delta"], 2)
    elif affinity_delta > 0:
        arc_update["trust_delta"] = max(arc_update["trust_delta"], 1)

    raw_scene = result.get("scene_update")
    if not isinstance(raw_scene, dict):
        raw_scene = {}
    scene_update = {
        "location": normalize_location(raw_scene.get("location")),
        "time": clean_optional_text(raw_scene.get("time")),
        "activity": clean_optional_text(raw_scene.get("activity")),
        "add_props": clean_string_list(raw_scene.get("add_props")),
        "remove_props": clean_string_list(raw_scene.get("remove_props")),
        "add_open_loops": clean_string_list(raw_scene.get("add_open_loops")),
        "close_open_loops": clean_string_list(raw_scene.get("close_open_loops")),
    }

    raw_life = result.get("life_update")
    if not isinstance(raw_life, dict):
        raw_life = {}
    life_update = {
        "current_goal": clean_optional_text(raw_life.get("current_goal"), 120),
        "current_problem": clean_optional_text(raw_life.get("current_problem"), 120),
        "next_plan": clean_optional_text(raw_life.get("next_plan"), 120),
        "recent_event": clean_optional_text(raw_life.get("recent_event"), 160),
    }
    if not reply or not isinstance(suggestions, list) or len(suggestions) < 2:
        raise ValueError("模型返回缺少回复或选项")
    if user_message_type not in {"dialogue", "action"}:
        user_message_type = "dialogue"
    if user_message_type == "dialogue":
        user_action_narration = ""
    else:
        user_action_narration = normalize_user_action_narration(user_action_narration, character)
    return {
        "reply": reply,
        "narration": narration,
        "suggestions": [clean_suggestion_text(item, character) for item in suggestions[:2]],
        "memory_updates": [
            normalized for item in memories[:3]
            if (normalized := normalize_memory_update(item)) is not None
        ] if isinstance(memories, list) else [],
        "topic": topic,
        "conversation_move": conversation_move,
        "interaction_pattern": interaction_pattern,
        "topic_domain": topic_domain,
        "initiative": initiative,
        "topic_source": topic_source,
        "affinity_update": affinity_update,
        "arc_update": arc_update,
        "scene_update": scene_update,
        "life_update": life_update,
        "user_message_type": user_message_type,
        "user_action_narration": user_action_narration,
    }


def infer_user_action(data: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    character = get_character(data)
    terms = character_terms(character)
    target = terms["character_pronoun"]
    name = re.escape(terms["name"])
    latest = str(data.get("latest_message", "")).strip()
    action_start = (
        r"^(?:我|你)?(?:[（(]|握住|牵住|拉住|抱住|靠近|凑近|凑过去|凑到|递给|喂给|抬手|低头|"
        rf"摸摸|亲吻|吻住|搂住|推开|引导{target}|看着{target}|走向{target}|走过去|坐到|站到|"
        rf"看屏幕|指向|问{target}|问{name}|告诉{target}|告诉{name}|对{target}说)"
    )
    action_clause = rf"[，,](?:然后|顺势|再)?(?:凑|靠|走|坐|站|伸手|抬手|问{target}|告诉{target}|对{target}说)"
    looks_like_action = bool(re.search(action_start, latest) or re.search(action_clause, latest))
    if looks_like_action:
        result["user_message_type"] = "action"
        if not result.get("user_action_narration"):
            action = latest.rstrip("。！？!?")
            result["user_action_narration"] = normalize_user_action_narration(action, character)
        else:
            result["user_action_narration"] = normalize_user_action_narration(
                result["user_action_narration"], character
            )
    else:
        result["user_message_type"] = "dialogue"
        result["user_action_narration"] = ""
    return result


def infer_interaction_pattern(data: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    latest = str(data.get("latest_message", "")).strip()
    reply = str(result.get("reply", "")).strip()
    user_escalation = r"那我(?:就|带|找|直接)|我就|我带|我找|我直接|看你|你敢"
    reply_escalation = r"那我(?:就|带|找|直接)|我就(?:用|带|找|画|叫|让)|我带|我找|我直接|看你怎么|你敢|迎战|反制|比赛|打[^，。！？]{0,8}仗"

    if re.search(user_escalation, latest) and re.search(reply_escalation, reply):
        result["interaction_pattern"] = "轻松对抗"
    elif re.search(r"难过|焦虑|害怕|压力|失眠|孤独|委屈|累|崩溃", latest):
        result["interaction_pattern"] = "情绪承接"
    elif result.get("life_update", {}).get("recent_event"):
        result["interaction_pattern"] = "生活分享"
    elif result.get("interaction_pattern") not in INTERACTION_PATTERNS:
        result["interaction_pattern"] = "信息交换" if "？" in reply or "?" in reply else "直接回应"
    return result


def compact_text(text: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff]", "", text).lower()


def text_similarity(left: str, right: str) -> float:
    a, b = compact_text(left), compact_text(right)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def validate_result(result: dict[str, Any], data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    character = get_character(data)
    terms = character_terms(character)
    reply = result["reply"]
    suggestions = result["suggestions"]
    latest = str(data.get("latest_message", "")).strip()
    compact_latest = compact_text(latest)
    compact_reply = compact_text(reply)

    if len(compact_latest) >= 6 and (
        compact_reply == compact_latest
        or (compact_latest in compact_reply and len(compact_reply) <= len(compact_latest) + 8)
        or text_similarity(latest, reply) >= 0.92
    ):
        errors.append("reply 复述了用户最新原句；请直接回应含义并加入新的态度或信息，不要回声式重复")

    history = data.get("messages", [])
    if isinstance(history, list):
        previous_replies = [
            str(item.get("text", "")).strip()
            for item in history[:-1]
            if isinstance(item, dict) and item.get("role") == "assistant"
        ]
        for old_reply in previous_replies[-16:]:
            similarity = text_similarity(reply, old_reply)
            compact_old = compact_text(old_reply)
            if (len(compact_reply) >= 6 and compact_reply == compact_old) or similarity >= 0.90:
                errors.append(
                    f"reply 与女主最近说过的话重复或过于近似（相似度 {similarity:.2f}）；必须针对用户最新问题提供新的具体内容"
                )
                break

    action_patterns = [
        rf"(?:{re.escape(terms['name'])}|{terms['character_pronoun']}|男生|女孩)[^。！？\n]{{0,28}}(?:愣|怔|咬|抿|垂|抬|靠|凑|握|牵|吻|笑|看|望|呼吸|眼神|耳尖|脸颊|下唇|手指)",
        r"(?:呼吸|眼神|眸|耳尖|脸颊|手指|唇角)[^。！？\n]{0,18}(?:一滞|加快|闪|躲|红|颤|收紧|扬起)",
        r"[（(][^）)]*(?:动作|神态|轻笑|脸红|靠近|低头)[^）)]*[）)]",
    ]
    if any(re.search(pattern, reply) for pattern in action_patterns):
        errors.append("reply 混入了第三人称动作、神态或环境描写；把这些内容移到 narration，reply 只保留林晚说出口的话")
    if reply_contains_assistant_action(reply):
        errors.append("reply 混入了林晚第一人称动作；动作必须移到 narration，reply 只保留说出口的话")

    errors.extend(suggestion_perspective_errors(reply, [str(item) for item in suggestions[:2]]))

    if len(suggestions) >= 2 and text_similarity(suggestions[0], suggestions[1]) >= 0.84:
        errors.append("两个 suggestions 含义过于相似；必须提供两个明显不同、但都能承接当前回复的方向")

    recent = data.get("recent_suggestions", [])
    if isinstance(recent, list):
        for suggestion in suggestions[:2]:
            for old in recent[-60:]:
                if text_similarity(str(suggestion), str(old)) >= 0.92:
                    errors.append(f"suggestion“{suggestion}”与最近展示过的选项重复或过于近似；请换一个新的表达和推进方向")
                    break

    if suggestions and any(compact_text(item) == compact_latest for item in suggestions[:2]):
        errors.append("suggestions 不能原样重复用户刚发出的消息")
    if result.get("user_message_type") == "action" and not result.get("user_action_narration"):
        errors.append("用户输入被判断为动作，但缺少 user_action_narration；请把用户动作改写成第二人称旁白")
    recent_patterns = [str(item) for item in data.get("recent_patterns", [])[-2:]]
    if recent_patterns == ["轻松对抗", "轻松对抗"] and result.get("interaction_pattern") == "轻松对抗":
        errors.append("已经连续两轮用玩笑反制继续加码；本轮应该收束玩法并转入具体生活、感受或关系含义")
    recent_initiatives = [str(item) for item in data.get("recent_initiatives", [])[-2:]]
    if recent_initiatives == ["自然回应", "自然回应"] and result.get("initiative") != active_initiative(data):
        errors.append("女主已连续两轮只做自然回应；本轮必须主动分享、观察、邀请、关系试探或切换话题")
    recent_domains = [str(item) for item in data.get("recent_topic_domains", [])[-2:]]
    if len(recent_domains) == 2 and recent_domains[0] == recent_domains[1] == result.get("topic_domain"):
        errors.append("同一话题域已经连续三轮；本轮必须切换到不同的成年男女关系话题")
    candidate_family = surface_family(f"{result.get('topic', '')} {reply}")
    if (
        candidate_family in saturated_surface_families(data)
        and not explicitly_requested_surface(latest, candidate_family)
        and result.get("topic_domain") not in TENSION_DOMAINS
    ):
        errors.append(f"{candidate_family}素材已重复出现；本轮必须彻底离开该素材并开启不同类型的话题或事件")
    if requires_tension_pivot(data) and result.get("topic_domain") not in TENSION_DOMAINS:
        errors.append("重复素材后的转场仍然过于日常；不能只换成吃饭、喝酒或散步，必须进入吸引力、关系试探、异性边界、感情经历或误会冲突")
    reply_opening = str(result.get("reply", "")).replace("\n", " ").strip()[:28]
    for old_opening in data.get("recent_reply_openings", [])[-80:]:
        old_text = str(old_opening).strip()
        if len(reply_opening) >= 10 and (
            text_similarity(reply_opening, old_text) >= 0.90
            or (len(old_text) >= 10 and (reply_opening.startswith(old_text) or old_text.startswith(reply_opening)))
        ):
            errors.append("reply 开头与长期历史中的表达过于相似；必须换一种具体回应方式，不能复用旧句式")
            break
    beat = str(result.get("arc_update", {}).get("last_beat", "")).strip()
    if beat and any(text_similarity(beat, str(old)) >= 0.90 for old in data.get("recent_story_beats", [])[-32:]):
        errors.append("arc_update.last_beat 重复了旧剧情节点；本轮必须产生新证据、新让步、新行动或新的关系含义")
    arc = data.get("arc") if isinstance(data.get("arc"), dict) else {}
    if arc.get("central_conflict") and result.get("topic_source") == "角色生活线" and not latest_is_substantive(latest):
        errors.append("当前矛盾尚未解决，不能无桥接跳到角色生活线；应先从矛盾、未完成事件或共同目标继续")
    return [adapt_character_text(error, data) for error in errors]


def hard_validation_errors(result: dict[str, Any], data: dict[str, Any]) -> list[str]:
    """Only defects severe enough to justify a second model request."""
    errors: list[str] = []
    reply = compact_text(result["reply"])
    latest = compact_text(str(data.get("latest_message", "")))
    if len(latest) >= 4 and reply == latest:
        errors.append("reply 完全照抄了用户最新消息")
    if reply_contains_assistant_action(str(result.get("reply", ""))):
        errors.append("reply 含有林晚第一人称动作；必须把动作移到 narration")

    history = data.get("messages", [])
    if isinstance(history, list):
        for item in history[:-1]:
            if isinstance(item, dict) and item.get("role") == "assistant":
                old = compact_text(str(item.get("text", "")))
                if len(reply) >= 6 and reply == old:
                    errors.append("reply 与女主历史回复完全相同")
                    break

        narration = str(result.get("narration", "")).strip()
        if narration:
            previous_narrations = [
                str(item.get("text", "")).strip()
                for item in history[:-1]
                if isinstance(item, dict) and item.get("role") == "narration"
            ]
            if any(text_similarity(narration, old) >= 0.90 for old in previous_narrations[-10:]):
                errors.append("narration 重复了最近已经显示过的场景提示；本轮应省略或描写真实的新变化")

    suggestions = [compact_text(str(item)) for item in result.get("suggestions", [])[:2]]
    if len(suggestions) >= 2 and suggestions[0] and suggestions[0] == suggestions[1]:
        errors.append("两个 suggestions 完全相同")
    recent = {
        compact_text(str(item))
        for item in data.get("recent_suggestions", [])[-60:]
        if compact_text(str(item))
    }
    if any(item in recent for item in suggestions):
        errors.append("suggestion 与最近展示的选项完全相同")
    errors.extend(suggestion_perspective_errors(
        str(result.get("reply", "")),
        [str(item) for item in result.get("suggestions", [])[:2]],
    ))
    recent_patterns = [str(item) for item in data.get("recent_patterns", [])[-2:]]
    if recent_patterns == ["轻松对抗", "轻松对抗"] and result.get("interaction_pattern") == "轻松对抗":
        errors.append("已经连续两轮轻松对抗；必须停止继续加码，转入具体生活、感受或关系含义")
    recent_initiatives = [str(item) for item in data.get("recent_initiatives", [])[-2:]]
    if recent_initiatives == ["自然回应", "自然回应"] and result.get("initiative") != active_initiative(data):
        errors.append("女主已连续两轮被动；本轮必须由女主主动推进")
    recent_domains = [str(item) for item in data.get("recent_topic_domains", [])[-2:]]
    if len(recent_domains) == 2 and recent_domains[0] == recent_domains[1] == result.get("topic_domain"):
        errors.append("同一话题域已连续三轮；必须主动换域")
    candidate_family = surface_family(f"{result.get('topic', '')} {result.get('reply', '')}")
    if (
        candidate_family in saturated_surface_families(data)
        and not explicitly_requested_surface(str(data.get("latest_message", "")), candidate_family)
        and result.get("topic_domain") not in TENSION_DOMAINS
    ):
        errors.append(f"{candidate_family}素材已经过度重复；必须换成完全不同的话题或事件")
    if requires_tension_pivot(data) and result.get("topic_domain") not in TENSION_DOMAINS:
        errors.append("素材疲劳后只换了普通日常活动；必须改为有男女关系张力的新话题或事件")
    if isinstance(history, list):
        previous_replies = [
            str(item.get("text", "")).strip()
            for item in history[:-1]
            if isinstance(item, dict) and item.get("role") == "assistant"
        ]
        if len(previous_replies) >= 2 and all(text.endswith(("?", "？")) for text in previous_replies[-2:]):
            if str(result.get("reply", "")).strip().endswith(("?", "？")):
                errors.append("女主连续三轮以问题结尾；本轮必须用陈述、主动分享或邀请推进")
    scene_age = int(data.get("scene_age_turns", 0) or 0)
    scene_update = result.get("scene_update", {})
    latest_text = str(data.get("latest_message", ""))
    new_location = str(scene_update.get("location", "")) if isinstance(scene_update, dict) else ""
    if relationship_focus(latest_text) and new_location and not user_requests_scene_change(latest_text):
        errors.append("用户正在谈关系，林晚却用换地点回避；必须留在当前场景正面回应")
    if new_location and re.search(DEFAULT_DESTINATION_PATTERN, new_location) and not re.search(DEFAULT_DESTINATION_PATTERN, latest_text):
        errors.append("又把工作室、画馆、画廊或咖啡馆当成万能目的地；必须结合时间与上下文换成新的合理选择")
    if new_location and re.search(r"还是|或者|你选|二选一", str(result.get("reply", ""))):
        errors.append("林晚仍在让用户选择场景，却提前写入了到达地点；用户选择前 scene_update.location 必须为空")
    if new_location and re.search(r"去哪|去哪里|接下来去|你想去哪|哪里合适", latest_text) and not any(
        keyword in latest_text for keyword in ("你决定", "你来选", "听你的")
    ):
        errors.append("用户只是在询问下一场景，还没有选定地点；应给出两个合理选项，不能替用户直接决定并写入 location")
    if scene_age >= 10 and not relationship_focus(latest_text) and not offers_scene_choices(result) and isinstance(scene_update, dict) and not any(
        scene_update.get(key) for key in ("location", "time", "activity", "add_open_loops", "close_open_loops")
    ):
        errors.append("当前场景停留过久；应提供两个上下文合理的场景选择，或在用户已选定时自然迁移")
    reply_opening = str(result.get("reply", "")).replace("\n", " ").strip()[:28]
    if any(
        len(reply_opening) >= 10 and (
            text_similarity(reply_opening, str(old)) >= 0.94
            or (len(str(old).strip()) >= 10 and (reply_opening.startswith(str(old).strip()) or str(old).strip().startswith(reply_opening)))
        )
        for old in data.get("recent_reply_openings", [])[-80:]
    ):
        errors.append("reply 复用了长期历史中的开头句式；必须针对本轮细节重写")
    arc_update = result.get("arc_update", {}) if isinstance(result.get("arc_update"), dict) else {}
    beat = str(arc_update.get("last_beat", "")).strip()
    if beat and any(text_similarity(beat, str(old)) >= 0.94 for old in data.get("recent_story_beats", [])[-32:]):
        errors.append("关系剧情节点与历史节点重复；必须推进新的证据、让步、行动或关系含义")
    current_arc = data.get("arc") if isinstance(data.get("arc"), dict) else {}
    current_phase = str(current_arc.get("phase", "试探"))
    next_phase = str(arc_update.get("phase", ""))
    if current_phase in ARC_PHASES and next_phase in ARC_PHASES:
        if ARC_PHASES.index(next_phase) > ARC_PHASES.index(current_phase) + 1:
            errors.append("关系阶段跨越过快；每轮最多推进一个阶段，不能从矛盾直接跳到亲密或确认")
    arc_age = int(data.get("turns", 0) or 0) - int(current_arc.get("started_at_turn", 0) or 0)
    if arc_update.get("resolved") is True and arc_age < 3 and not re.search(r"道歉|我承认|说清楚|误会解开|解决", latest_text):
        errors.append("核心矛盾解决得过快；至少先交换立场并完成一次可见行动")
    return [adapt_character_text(error, data) for error in errors]


def parse_model_json(
    content: str, character: dict[str, Any] | None = None
) -> dict[str, Any]:
    cleaned = content.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("模型没有返回可解析的 JSON")
        result = json.loads(match.group(0))

    if not isinstance(result, dict):
        raise ValueError("模型返回格式不是对象")
    return normalize_result(result, character)


def repair_model_output(
    raw_content: str,
    original_messages: list[dict[str, str]],
    character: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repair_messages = [
        {
            "role": "system",
            "content": (
                "把给定内容整理成合法 JSON，只做格式整理，不增加新剧情。必须包含 reply、narration、suggestions、"
                "memory_updates、topic、conversation_move、interaction_pattern、topic_domain、initiative、topic_source、arc_update、scene_update、life_update、"
                "user_message_type、user_action_narration；suggestions 必须有两个符合上下文的用户回复。"
            ),
        },
        {"role": "user", "content": "需要整理的原始输出：\n" + (raw_content or "（原输出为空，请依据最后一轮上下文重新生成）")},
        {"role": "system", "content": "最后一轮上下文：" + json.dumps(original_messages[-6:], ensure_ascii=False)},
    ]
    payload = request_model(repair_messages, temperature=0.4, max_tokens=600)
    content = extract_content(payload)
    return parse_model_json(content, character)


def regenerate_after_format_failure(
    original_messages: list[dict[str, str]],
    failure: str,
    character: dict[str, Any] | None = None,
) -> dict[str, Any]:
    character = character or get_character()
    terms = character_terms(character)
    context = json.dumps(original_messages[-12:], ensure_ascii=False)
    retry_messages = [
        {
            "role": "system",
            "content": (
                f"你是{terms['name']}，{character['age']}岁，{character['city']}{character['occupation']}。根据给定聊天上下文自然回复用户最后一句。"
                "不要复读用户，不要使用客服话术。台词只写说出口的话，动作放旁白。"
                "不要输出JSON或代码块。严格按以下八行纯文本输出，每个标签只出现一次：\n"
                + f"REPLY: {terms['name']}说出口的话\n"
                + "NARRATION: 场景旁白，没有则写NONE\n"
                + "OPTION_A: 用户可选回复A\n"
                + "OPTION_B: 用户可选回复B\n"
                + "TOPIC: 核心话题\n"
                + "MOVE: 本轮采用的推进方式\n"
                + "TOPIC_DOMAIN: 关系试探等规定话题域\n"
                + f"INITIATIVE: {terms['lead']}主动或自然回应\n"
                + "USER_TYPE: dialogue或action\n"
                + "USER_ACTION: 用户动作旁白，没有则写NONE"
            ),
        },
        {"role": "user", "content": "聊天上下文：" + context + "\n上次格式错误：" + failure},
    ]
    payload = request_model(retry_messages, temperature=0.7, max_tokens=500, json_mode=False)
    return parse_tagged_output(extract_content(payload), character)


def parse_tagged_output(
    content: str, character: dict[str, Any] | None = None
) -> dict[str, Any]:
    fields: dict[str, str] = {}
    for line in content.strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().upper()] = value.strip()
    reply = fields.get("REPLY", "")
    option_a = fields.get("OPTION_A", "")
    option_b = fields.get("OPTION_B", "")
    if not reply or not option_a or not option_b:
        raise ValueError("模型纯文本修复结果缺少必要字段")
    return normalize_result({
        "reply": reply,
        "narration": "" if fields.get("NARRATION", "").upper() == "NONE" else fields.get("NARRATION", ""),
        "suggestions": [option_a, option_b],
        "memory_updates": [],
        "topic": fields.get("TOPIC", "闲聊"),
        "conversation_move": fields.get("MOVE", "自然承接"),
        "topic_domain": fields.get("TOPIC_DOMAIN", "生活目标"),
        "initiative": fields.get("INITIATIVE", "自然回应"),
        "user_message_type": fields.get("USER_TYPE", "dialogue").lower(),
        "user_action_narration": "" if fields.get("USER_ACTION", "").upper() == "NONE" else fields.get("USER_ACTION", ""),
    }, character)


def parse_model_output(
    content: str, character: dict[str, Any] | None = None
) -> dict[str, Any]:
    stripped = content.strip()
    if stripped.startswith("{") or stripped.startswith("```json"):
        return parse_model_json(content, character)
    return parse_tagged_output(content, character)


def rewrite_invalid_result(
    result: dict[str, Any],
    errors: list[str],
    original_messages: list[dict[str, str]],
    data: dict[str, Any],
) -> dict[str, Any]:
    character = get_character(data)
    rewrite_messages = [
        {
            "role": "system",
            "content": adapt_character_text(
                (
                "你是对话质量编辑器，负责把林晚的一轮失败回复整轮重写成合法 JSON。"
                "失败回复只能作为反例，禁止照抄句式、笑点和选项。reply 只能是林晚说出口的话。"
                "当错误涉及连续轻松对抗时：最多用半句话承认用户的玩笑，随后必须回到当前场景、"
                "林晚的具体生活、真实感受或双方关系含义；禁止继续提出更强装备、迎战、反制、"
                "比赛和‘那我就’式升级。interaction_pattern 不得为‘轻松对抗’，两个 suggestions "
                "也不得继续加码。若错误涉及女主被动，必须先加入林晚自己的具体态度、偏好或决定，再发起邀请、"
                "关系试探或换话题，并将 initiative 设为‘女主主动’。若错误涉及话题重复，topic_domain 必须换成"
                "最近没有使用的域。若错误涉及场景停滞，必须通过可见行动自然迁移并填写 scene_update。"
                "若 reply 混入第一或第三人称动作，把动作改写进 narration，reply 只留台词。若 narration 重复，"
                "删除它或只写本轮真实的新动作。若 suggestions 主语颠倒，严格按用户视角纠正谁教谁、谁请谁。"
                "若错误涉及摄影绘画、咖啡馆或雨天素材疲劳，重写内容必须完全避开该素材，不能换同义词继续聊，"
                "也不能只换成吃饭、喝酒或散步；必须转向吸引力、偏爱、嫉妒、异性边界、过去感情、谁更主动或带误会的新事件，topic_domain 使用对应的关系类枚举。"
                "若用户正在问喜欢、在意、吃醋或关系，必须留在原地直接回答，禁止借换场回避。若需要换场但用户没有选，"
                "给出两个结合时间和上下文的反差场景，两个 suggestions 分别对应选择，scene_update.location 留空；用户选定后才能迁移。"
                "禁止再次默认去工作室、画馆、画廊或咖啡馆。"
                "主动话题必须来自用户当前话语、当前矛盾、未完成事件、共同约定、长期记忆或角色生活线，"
                "不得随机跳题。arc_update 必须记录本轮新增节点，不能一轮解决长期矛盾。"
                "scene_update 和 life_update 只记录本轮真实发生的变化。只输出 JSON。"
                ),
                data,
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "最近上下文": original_messages[-8:],
                    "失败回复": result,
                    "必须修复的问题": [adapt_character_text(error, data) for error in errors],
                    "最近选项": data.get("recent_suggestions", [])[-40:],
                    "最近话题域": data.get("recent_topic_domains", [])[-8:],
                    "最近主动性": data.get("recent_initiatives", [])[-6:],
                    "最近话题来源": data.get("recent_topic_sources", [])[-12:],
                    "最近剧情节点": data.get("recent_story_beats", [])[-24:],
                    "禁止复用的回复开头": data.get("recent_reply_openings", [])[-60:],
                    "本轮禁用的疲劳素材": saturated_surface_families(data),
                    "当前场景": data.get("scene", {}),
                    "当前关系弧线": data.get("arc", {}),
                    "当前场景轮数": data.get("scene_age_turns", 0),
                    "成熟暧昧模式": data.get("mature_mode") is True and data.get("adult_confirmed") is True,
                },
                ensure_ascii=False,
            ),
        },
    ]
    payload = request_model(rewrite_messages, temperature=0.62, max_tokens=750, json_mode=True)
    return parse_model_json(extract_content(payload), character)


def fallback_suggestions(result: dict[str, Any], data: dict[str, Any]) -> list[str]:
    latest = str(data.get("latest_message", ""))
    if int(data.get("scene_age_turns", 0) or 0) >= 8 and not user_requests_scene_change(latest):
        places = [item.split("：", 1)[0] for item in scene_candidates(data)[:2]]
        candidates = [f"去{places[0]}吧，我想看看那里会发生什么。", f"我更想选{places[1]}，换种气氛继续聊。"]
    elif result.get("topic_domain") in TENSION_DOMAINS or relationship_focus(latest):
        candidates = [
            "先别换话题，我想听你把真实想法说完。",
            "那我也认真回答，不过你得先说清楚你最在意什么。",
            "我接受你的答案，但我还想知道你会不会只对我这样。",
            "地点先不急着定，我们先把彼此的边界说清楚。",
        ]
    else:
        candidates = [
            "这次由你主动选一个完全不同的话题。",
            "先留在这里，把刚才没说完的那句说完。",
            "我想听一件和工作无关、但很像你的事。",
            "我们换个玩法，各说一个不太愿意承认的偏好。",
        ]
    recent = [str(item) for item in data.get("recent_suggestions", [])[-60:]]
    chosen: list[str] = []
    for candidate in candidates:
        if all(text_similarity(candidate, old) < 0.88 for old in recent + chosen):
            chosen.append(candidate)
        if len(chosen) == 2:
            return chosen
    return candidates[:2]


def stabilize_result_after_rewrite_failure(
    result: dict[str, Any], data: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    """Apply deterministic repairs so a usable first response is not discarded."""
    stable = normalize_result(result, get_character(data))
    joined = " | ".join(errors)

    if "narration 重复" in joined:
        stable["narration"] = ""
    if any(token in joined for token in ("suggestion", "suggestions", "选项")):
        stable["suggestions"] = fallback_suggestions(stable, data)
    if "同一话题域" in joined or "主动换域" in joined:
        stable["topic_domain"] = choose_fallback_domain(stable, data)

    scene_errors = ("场景", "地点", "location", "万能目的地", "换地点回避")
    if any(token in joined for token in scene_errors):
        scene_update = dict(stable.get("scene_update", {}))
        scene_update["location"] = ""
        stable["scene_update"] = scene_update
        if int(data.get("scene_age_turns", 0) or 0) >= 8:
            stable["suggestions"] = fallback_suggestions(stable, data)

    arc_update = dict(stable.get("arc_update", {}))
    current_arc = data.get("arc") if isinstance(data.get("arc"), dict) else {}
    if "关系阶段跨越过快" in joined:
        arc_update["phase"] = str(current_arc.get("phase", "试探"))
    if "核心矛盾解决得过快" in joined:
        arc_update["resolved"] = False
    if "剧情节点" in joined:
        arc_update["last_beat"] = ""
    stable["arc_update"] = arc_update
    return stable


def memory_search_text(data: dict[str, Any]) -> str:
    parts = [str(data.get("latest_message", ""))]
    history = data.get("messages", [])
    if isinstance(history, list):
        parts.extend(
            str(item.get("text", ""))
            for item in history[-8:]
            if isinstance(item, dict)
        )
    scene = data.get("scene", {})
    if isinstance(scene, dict):
        parts.extend(str(scene.get(key, "")) for key in ("location", "activity"))
    return "\n".join(parts)


def prepare_memory_context(data: dict[str, Any]) -> tuple[dict[str, Any], str]:
    namespace = normalize_namespace(data.get("memory_id"))
    if not namespace:
        return data, ""
    WORLD_BOOK.import_legacy(namespace, data.get("memories", []))
    enriched = dict(data)
    enriched["retrieved_memories"] = WORLD_BOOK.search(
        namespace, memory_search_text(data), limit=8
    )
    return enriched, namespace


def persist_result_memories(result: dict[str, Any], namespace: str) -> dict[str, Any]:
    if not namespace:
        return result
    result["stored_memories"] = WORLD_BOOK.apply_updates(
        namespace, result.get("memory_updates", [])
    )
    return result


def call_model(data: dict[str, Any]) -> dict[str, Any]:
    if not AI_API_KEY:
        raise RuntimeError("尚未配置 DeepSeek API Key。请复制 .env.example 为 .env，填入 AI_API_KEY 后重启服务。")

    data = sanitize_chat_payload(data)
    request_started = time.monotonic()
    latest = str(data.get("latest_message", ""))
    data, memory_namespace = prepare_memory_context(data)
    character = get_character(data)
    log_event(f"chat start turns={data.get('turns', 0)} chars={len(latest)}")
    messages = build_messages(data)
    used_retry = False
    payload = request_model(messages, temperature=0.72, max_tokens=750, json_mode=True)
    raw_content = extract_content(payload)
    try:
        result = parse_model_output(raw_content, character)
    except (ValueError, json.JSONDecodeError) as exc:
        used_retry = True
        try:
            result = repair_model_output(raw_content, messages, character)
        except (ValueError, json.JSONDecodeError) as retry_exc:
            raise RuntimeError("DeepSeek 本轮响应不完整，格式修复后仍未成功，请重新发送。") from retry_exc
    result = infer_interaction_pattern(data, infer_user_action(data, result))

    quality_notes = validate_result(result, data)
    hard_errors = hard_validation_errors(result, data)
    if not hard_errors:
        notes = " | ".join(quality_notes) if quality_notes else "none"
        log_event(
            f"chat complete elapsed={time.monotonic() - request_started:.2f}s "
            f"format_repaired={int(used_retry)} rewritten=0 notes={notes}"
        )
        return persist_result_memories(result, memory_namespace)

    if hard_errors:
        fallback_candidate = result
        try:
            rewritten = infer_interaction_pattern(
                data,
                infer_user_action(data, rewrite_invalid_result(result, hard_errors, messages, data)),
            )
            fallback_candidate = rewritten
            remaining_errors = hard_validation_errors(rewritten, data)
            domain_errors = [error for error in remaining_errors if "同一话题域" in error]
            if remaining_errors and len(domain_errors) == len(remaining_errors):
                rewritten["topic_domain"] = choose_fallback_domain(rewritten, data)
                remaining_errors = hard_validation_errors(rewritten, data)
            suggestion_errors = [error for error in remaining_errors if "suggestion" in error or "suggestions" in error]
            if remaining_errors and len(suggestion_errors) == len(remaining_errors):
                rewritten["suggestions"] = fallback_suggestions(rewritten, data)
                remaining_errors = hard_validation_errors(rewritten, data)
            if remaining_errors:
                raise ValueError("定向重写仍未通过：" + " | ".join(remaining_errors))
            log_event(
                f"chat complete elapsed={time.monotonic() - request_started:.2f}s "
                f"format_repaired={int(used_retry)} rewritten=1"
            )
            return persist_result_memories(rewritten, memory_namespace)
        except (ValueError, json.JSONDecodeError, RuntimeError) as exc:
            fallback = stabilize_result_after_rewrite_failure(fallback_candidate, data, hard_errors)
            log_event(
                f"chat rewrite degraded elapsed={time.monotonic() - request_started:.2f}s "
                f"reason={str(exc)[:240]}"
            )
            return persist_result_memories(fallback, memory_namespace)


def status_payload() -> dict[str, Any]:
    return {"configured": bool(AI_API_KEY), "model": AI_MODEL, "version": APP_VERSION}


Handler = create_handler(
    root=ROOT,
    chat=call_model,
    status=status_payload,
    logger=log_event,
    model_slots=MODEL_SLOTS,
)
