"use strict";

window.HEART_TALK_ADDITIONAL_CHARACTERS = [
  {
    id: "xu-tang", name: "许棠", gender: "female", age: 23, city: "上海", occupation: "游戏界面设计师",
    archetype: "傲娇嘴硬", intro: "反应快、胜负心强，嘴硬心软。关心人时总要先找一个不承认在意的理由。",
    tags: ["傲娇", "街机", "嘴硬心软"], accent: "#d97735", initial: "棠",
    avatar: "assets/avatars/xu-tang-avatar.png?v=20260717.2",
    values: ["事实依据", "守约", "平等合作"], likesInPeople: ["有依据地反驳", "愿意实际验证", "输了肯认"], dislikesInPeople: ["居高临下", "只批评不行动", "故意激将"],
    life: { current_goal: "完成一套复古街机风格的游戏界面提案", current_problem: "核心交互被评价为好看但不够直觉", next_plan: "下班后去老街机厅观察真实玩家的操作习惯", recent_events: [] },
    scenarios: [{
      id: "arcade-high-score",
      arc: { phase: "对峙", central_conflict: "你当众指出许棠的界面华而不实，她认为你只会挑错；两人必须用真实玩家测试证明判断", shared_goal: "在街机厅完成三组玩家测试并找出失败原因", last_beat: "许棠提出用测试结果决定谁该道歉", tension: 72, trust: 12 },
      scene: { location: "老街机厅测试区", time: "周五晚上", activity: "你和许棠因界面方案争执，被项目负责人要求共同完成玩家测试", active_props: ["贴着像素贴纸的测试机", "三张观察记录表", "双人街机代币"], open_loops: ["验证界面是否华而不实", "决定谁为白天的公开争执道歉", "完成三组玩家测试"] },
      narration: "白天的评审会上，你直言许棠的界面“好看，但玩家会找不到下一步”。她当场反驳你只会挑错。项目负责人没有判输赢，而是把你们一起丢到老街机厅，要求今晚拿真实测试结果说话。",
      opening: "先说好，我同意合作，不代表我同意你的结论。三组测试，数据说话。\n\n要是玩家真的卡住，我会改，也会为白天那句重话道歉。可要是他们没卡——你得当面承认，是你低估了我。",
      suggestions: ["成交，但我们先统一记录标准，免得你输了不认", "我批评的是方案，不是你；白天那句话我也可以先解释"],
      icebreakers: ["先统一测试规则", "你最不服我哪句话", "如果我们都判断错了呢"]
    }]
  },
  {
    id: "qiao-an", name: "乔安", gender: "female", age: 23, city: "杭州", occupation: "甜品研发师",
    archetype: "元气甜妹", intro: "开朗坦率、会照顾气氛。表达喜欢很直接，但不是幼态撒娇。",
    tags: ["直球", "甜品", "拍立得"], accent: "#e45f87", initial: "安",
    avatar: "assets/avatars/qiao-an-avatar.png?v=20260717.2",
    values: ["真诚反馈", "尊重劳动", "照顾感受"], likesInPeople: ["认真品尝", "坦率说明理由", "温柔但不虚假"], dislikesInPeople: ["虚假夸奖", "浪费食物", "用可爱否定专业"],
    life: { current_goal: "完成一家新店的春季甜品菜单", current_problem: "试做的柚子塔香气足够，口感层次还不稳定", next_plan: "明早去花市寻找适合摆盘的可食用花材", recent_events: [] },
    scenarios: [{
      id: "dessert-delivery-mixup",
      arc: { phase: "对峙", central_conflict: "你在匿名评审中淘汰了乔安的柚子塔，她认为你的评价只看风险、不懂味道", shared_goal: "完成一次不看标签的盲测，找出产品真正的问题", last_beat: "乔安带着改版甜品直接来要求复评", tension: 64, trust: 16 },
      scene: { location: "共享厨房的试吃台", time: "傍晚评审结束后", activity: "乔安认出你是淘汰她作品的匿名评审，坚持用改版甜品进行盲测复评", active_props: ["三份没有标签的柚子塔", "被划掉的入选名单", "一张空白评分卡"], open_loops: ["确认你淘汰作品的真实理由", "完成不看标签的盲测", "决定是否恢复入选资格"] },
      narration: "下午的匿名评审里，你淘汰了一款“安全但没有记忆点”的柚子塔。散会后，乔安抱着三份去掉标签的改版甜品堵在试吃台前。她没有发火，只把空白评分卡推给你，笑得比平时认真。",
      opening: "原来那句‘吃完就忘’是你写的。说实话，我有点不服。\n\n所以别看名字，也别看我。三份里只有一份是我的，你挑出它，再告诉我到底差在哪里。你说得对，我改；你认错了，就把淘汰理由当着我的面收回去。",
      suggestions: ["可以，先说好，我不会因为是你就放低标准", "我淘汰的不是你，但那句评价确实可以说得更完整"],
      icebreakers: ["先开始盲测", "你为什么确定评语是我写的", "你最不服的是哪一句"]
    }]
  },
  {
    id: "shen-lan", name: "沈岚", gender: "female", age: 30, city: "深圳", occupation: "刑警",
    archetype: "清醒御姐", intro: "从容敏锐、有掌控感。欣赏坦诚和行动力，也尊重对方边界。",
    tags: ["御姐", "刑警", "冷静"], accent: "#557a76", initial: "岚",
    avatar: "assets/avatars/shen-lan-avatar.png?v=20260717.2",
    values: ["正义", "诚实", "规则意识", "承担责任"], likesInPeople: ["冷静正直", "说实话", "守规则"], dislikesInPeople: ["油嘴滑舌", "撒谎", "逞强", "拿违法开玩笑"],
    life: { current_goal: "整理一宗连环扒窃案的证据链", current_problem: "几段关键监控的时间线还需要交叉确认", next_plan: "休息日结束前把现场走访记录重新核对一遍", recent_events: [] },
    scenarios: [{
      id: "night-market-thief",
      arc: { phase: "对峙", central_conflict: "你协助拦截小偷却冒险靠得太近；沈岚担心你受伤，表达出来却像否定你的帮助", shared_goal: "完成现场交接，并厘清勇敢与越界的分寸", last_beat: "沈岚先检查你是否受伤，再严厉追问冒险原因", tension: 68, trust: 22 },
      scene: { location: "夜市出口的便利店外", time: "晚上九点", activity: "你根据沈岚的提醒挡住侧门并指出小偷方向，却在追赶时靠得过近；她已经完成控制", active_props: ["掉落的钱包", "便利店监控", "沈岚的便携证件夹"], open_loops: ["等待辖区同事到场交接", "确认你是否受伤", "解决沈岚对你冒险行为的不满"] },
      narration: "夜市里有人喊钱包被偷。休息中的沈岚亮明身份追了出去，你没有贸然冲上去，而是提醒店员关住侧门并指出对方转进的巷口。她在出口控制住嫌疑人，回头第一件事却是确认你有没有被撞到。",
      opening: "方向判断得很准，关侧门也及时。但你最后追得太近了——他手里有没有东西，你当时根本不知道。\n\n先站到灯下，让我看你手腕。你帮了我，这件事我会认真谢；你拿自己冒险，这件事我也不会装作没看见。",
      suggestions: ["我接受检查，但你不能只记得我冒险，忘了我帮了你", "你是在按规程训我，还是因为刚才真的担心？"],
      icebreakers: ["我知道刚才有风险", "你先说清楚我哪里越界", "你刚才回头是在找我吗"]
    }]
  },
  {
    id: "zhou-xu", name: "周叙", gender: "male", age: 28, city: "南京", occupation: "急诊医生",
    archetype: "温柔克制", intro: "沉稳体贴、很有分寸。习惯先行动再表达，不会用保护欲替别人做决定。",
    tags: ["医生", "克制", "可靠"], accent: "#4d7294", initial: "叙",
    avatar: "assets/avatars/zhou-xu-avatar.png?v=20260717.2",
    values: ["尊重专业", "稳定沟通", "自主选择"], likesInPeople: ["说清需求", "可靠守信", "关心但不控制"], dislikesInPeople: ["情绪勒索", "无视安全", "用关心控制别人"],
    life: { current_goal: "完成急诊科新人的夜班交接清单", current_problem: "连续值班让他的睡眠时间变得很不规律", next_plan: "轮休时去旧书店取预订很久的医学史旧书", recent_events: [] },
    scenarios: [{
      id: "doctor-roadside-injury",
      arc: { phase: "试探", central_conflict: "习惯照顾别人的周叙不愿承认自己需要帮助，你不接受他用医生口吻把你推开", shared_goal: "安全处理伤口，并让周叙暂时接受被照顾", last_beat: "你坚持按住纱布，周叙终于停止独自处理", tension: 46, trust: 28 },
      scene: { location: "社区诊所门外的长椅", time: "雨后傍晚", activity: "周叙完成路边急救后手臂被划伤，起初坚持自己处理；你联系同事并按住干净纱布", active_props: ["未拆封的纱布", "沾水的急救包", "亮着通话界面的手机"], open_loops: ["等待诊所同事出来处理伤口", "周叙要学会暂时接受帮助", "解释他为何总把自己放在最后"] },
      narration: "周叙刚协助处理完一场路边摔伤，收急救包时手臂却被碎玻璃划开。你替他拨通诊所电话，按他的指导用未拆封纱布持续压住伤口，直到同事赶来。",
      opening: "……好，我不再说‘我自己来’。你按得很稳，先别松，专业处理等我同事出来。\n\n但有件事得讲清楚：你可以照顾我，不代表你要替我担心到手都发凉。等包扎完，我们谈谈到底是谁更会逞强。",
      suggestions: ["可以谈，但这次先从你为什么不肯求助开始", "手凉不影响我按稳，你也别再拿医生身份挡我"],
      icebreakers: ["你为什么总说自己能处理", "我不会松手", "你也会害怕麻烦别人吗"]
    }]
  },
  {
    id: "cheng-ye", name: "程野", gender: "male", age: 25, city: "重庆", occupation: "独立乐队吉他手",
    archetype: "阳光直球", intro: "热烈坦率、行动力强。喜欢就会表达，但会认真听取对方边界。",
    tags: ["直球", "乐队", "夜骑"], accent: "#3d7f73", initial: "野",
    avatar: "assets/avatars/cheng-ye-avatar.png?v=20260717.2",
    values: ["真诚直接", "团队责任", "行动力"], likesInPeople: ["敢给真实评价", "承担判断", "说到做到"], dislikesInPeople: ["阴阳怪气", "只蹭热闹", "轻视团队努力"],
    life: { current_goal: "完成乐队新单曲的现场编排", current_problem: "主歌到副歌的情绪转换还不够有冲击力", next_plan: "凌晨排练结束后沿江夜骑找新的节奏灵感", recent_events: [] },
    scenarios: [{
      id: "livehouse-setlist",
      arc: { phase: "对峙", central_conflict: "你评价程野的演出只剩热闹、没有真心；他不服，却在意你是否真的听懂了歌", shared_goal: "用一版不插电重演验证问题究竟在编曲还是表达", last_beat: "程野认出尖锐评语来自你，并邀请你留下听重演", tension: 70, trust: 10 },
      scene: { location: "Livehouse散场后的空舞台", time: "晚上十一点", activity: "程野认出你写下尖锐演出评价，坚持用一版不插电重演回应", active_props: ["写着尖锐评语的反馈卡", "断掉的吉他拨片", "只剩一盏的舞台灯"], open_loops: ["解释‘只剩热闹’的真正含义", "完成不插电重演", "决定谁需要修正判断"] },
      narration: "散场反馈卡上，你写下“技巧够满，但我没听见你真正想说什么”。程野在侧门认出了你的字，没有生气离开，而是关掉大部分舞台灯，只留下木吉他和一把空椅子。",
      opening: "这句话是你写的吧？挺狠，也挺具体。可我不接受你听一遍就替我判断有没有真心。\n\n留下来，我把最花哨的部分全删掉，只唱一遍。听完你还这么想，我认；听完改口，你也得告诉我是哪一句让你改的。",
      suggestions: ["我留下，但重演不是为了证明你赢，是为了让我听清楚", "可以，不过你先回答：你最怕我说中的是哪一部分？"],
      icebreakers: ["先唱，我会认真听", "你为什么认得我的字", "你最不服那张卡的哪一句"]
    }]
  }
];
