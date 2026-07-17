"use strict";

const LEGACY_STORAGE_KEY = "heart-talk-ai-v1";
const CHARACTER_SELECTION_KEY = "heart-talk-selected-character";
const STORAGE_KEY_PREFIX = "heart-talk-ai-v2";
const API_ORIGIN = window.location.origin;

const INITIAL_SCENARIOS = [
  {
    id: "gallery-misunderstanding",
    arc: { phase: "试探", central_conflict: "林晚误会你拿走未公开画稿，也因衬衫赔偿欠你一个解释", shared_goal: "搬完最后一箱画，并重新建立基本信任", last_beat: "误会刚刚澄清，林晚主动提出补偿", tension: 52, trust: 24 },
    scene: {
      location: "独立画廊后门",
      time: "闭馆后的晚上",
      activity: "你帮林晚找回误装进纸箱的画稿，刚解开一场误会",
      active_props: ["散落的画稿", "沾到颜料的衬衫", "画展工作证"],
      open_loops: ["林晚要赔你被颜料弄脏的衬衫", "一起把最后一箱画搬回工作室"]
    },
    narration: "闭馆后，林晚发现一叠未公开画稿不见了。她追到后门才看见你正把误装进纸箱的画一张张捡回来，也看见自己刚才撞翻的颜料沾上了你的袖口。",
    opening: "刚才是我误会你了，先道歉。还有你袖口那块颜料……我赔你一件，还是请你去我工作室喝一杯，慢慢谈赔偿？\n\n不过先说好，我不是对每个帮我捡画的人都这么主动。",
    suggestions: ["一件衬衫不够，至少还欠我一顿夜宵", "你刚才追出来的时候，好像不只是担心画"],
    icebreakers: ["先说说你为什么误会我", "工作室离这里远吗", "你平时也这么主动道歉？"]
  },
  {
    id: "wrong-blind-date",
    arc: { phase: "试探", central_conflict: "林晚认错相亲对象，却发现你认真回答了她的私人问题", shared_goal: "在真正相亲对象出现前弄清彼此是否愿意继续认识", last_beat: "身份误会被揭开，但两人都没有立刻离开", tension: 44, trust: 18 },
    scene: {
      location: "街角咖啡馆靠窗的位置",
      time: "周六下午",
      activity: "林晚坐错桌，把你误认成朋友安排的相亲对象",
      active_props: ["两杯放凉的咖啡", "写错名字的预订牌", "林晚的速写本"],
      open_loops: ["真正的相亲对象还没有出现", "林晚已经问了你一个很私人的恋爱问题"]
    },
    narration: "林晚在你对面坐了两分钟，认真问完“介不介意女朋友凌晨改稿”，才看见桌上的预订牌不是她要找的名字。",
    opening: "你不是陈放？那我刚才问你那么私人的问题，你怎么还答得那么认真？\n\n既然都聊到这了，你现在走，反而像临阵逃跑。至少告诉我，刚才那个答案是不是只说给相亲对象听的。",
    suggestions: ["如果对象是你，我的答案可以再认真一点", "你发现认错人以后，为什么没有马上走？"],
    icebreakers: ["你刚才问得确实很像相亲", "真正那个人来了怎么办", "那我也问你一个私人问题"]
  },
  {
    id: "studio-stairs",
    arc: { phase: "试探", central_conflict: "林晚因门锁把你困在楼梯间，不想让感谢变成敷衍的人情", shared_goal: "等待备用钥匙，并决定这段意外是否算一次约会", last_beat: "林晚提出去楼顶或留下喝酒", tension: 35, trust: 30 },
    scene: {
      location: "插画工作室六楼的楼梯间",
      time: "夜里十点",
      activity: "电梯停运，你帮林晚把大画框搬上六楼，工作室门却意外反锁",
      active_props: ["一人高的画框", "反锁的工作室门", "便利店袋子"],
      open_loops: ["等房东送备用钥匙", "林晚欠你一次正式的感谢"]
    },
    narration: "夜里十点，工作室电梯停运。你帮林晚把画框搬上六楼，刚放下，工作室的门却在身后咔哒一声反锁了。",
    opening: "你帮我搬了六层，现在还被我连累得回不了工作室。我要是只说谢谢，显得挺没诚意。\n\n楼顶有风，便利店袋子里还有两罐酒。你选一个，我陪你把这段倒霉时间过得像约会一点。",
    suggestions: ["去楼顶，但酒要你亲手递给我", "先说清楚，你对谁都会把感谢变成约会吗？"],
    icebreakers: ["那就去楼顶吹会儿风", "我更想知道你画了什么", "这算是你主动约我吗？"]
  },
  {
    id: "bookstore-note",
    arc: { phase: "对峙", central_conflict: "林晚误读便签并短暂心动，你必须说明那句话原本写给谁", shared_goal: "说清便签归属，并决定最后一本画册给谁", last_beat: "林晚承认自己白心动了几秒", tension: 48, trust: 14 },
    scene: {
      location: "旧书店二楼的窄走廊",
      time: "傍晚停电刚恢复",
      activity: "林晚拿错了你的书，把扉页便签误认为你写给她的话",
      active_props: ["夹着便签的旧电影画册", "林晚抱错的书", "应急手电"],
      open_loops: ["解释便签真正写给谁", "决定最后一本画册归谁"]
    },
    narration: "旧书店短暂停电。灯亮以后，林晚才发现自己抱错了你的画册，还读到了扉页那句“别总一个人看完结局”。",
    opening: "所以这张便签不是写给我的？……有点尴尬，我刚才还认真想了半天该怎么回答你。\n\n书可以还你，但那句话让我白心动了几秒。这笔账，你准备怎么算？",
    suggestions: ["现在写给你也来得及", "你刚才想怎么回答？我比较想听这个"],
    icebreakers: ["那句话现在算写给你", "你刚才真的心动了？", "最后一本书可以让给你"]
  },
  {
    id: "access-card",
    arc: { phase: "对峙", central_conflict: "林晚误把还门禁卡的你当成跟踪者，警惕与短暂期待同时存在", shared_goal: "在末班车到来前澄清误会并决定是否同行", last_beat: "林晚道歉，却承认自己曾期待另一种理由", tension: 60, trust: 12 },
    scene: {
      location: "末班地铁入口旁",
      time: "晚上十一点前",
      activity: "你追了半条街归还林晚掉落的工作室门禁卡，她起初误会你在跟着她",
      active_props: ["工作室门禁卡", "即将停运的地铁提示", "林晚没电的手机"],
      open_loops: ["最后一班地铁即将进站", "林晚想补偿你追来的这段路"]
    },
    narration: "你追了半条街，终于在地铁口叫住林晚。她警惕地回头，直到看见你手里那张从她包里滑落的工作室门禁卡。",
    opening: "原来你追过来只是为了还卡。抱歉，我刚才差点把你当成跟踪我的人。\n\n不过你跑得这么认真，害我白紧张了半分钟……也白期待了一秒。末班车还有四分钟，你要我现在解释那一秒吗？",
    suggestions: ["车可以等下一班，那一秒先解释清楚", "你期待的是我追你，还是期待我有别的理由？"],
    icebreakers: ["那一秒你期待了什么", "先上车，路上慢慢解释", "你准备怎么补偿我？"]
  },
  {
    id: "rooftop-sketches",
    arc: { phase: "试探", central_conflict: "林晚否认画中侧脸最初来自你，却迟迟没有松开你的手", shared_goal: "说清画像来源，并决定是否承认已经产生的关注", last_beat: "林晚让你在真话和面子之间选择", tension: 42, trust: 26 },
    scene: {
      location: "商业楼天台",
      time: "日落前",
      activity: "一阵风吹散林晚的速写，你帮她拦下最后一张，也顺手拉住了她",
      active_props: ["被风吹散的速写", "卡在围栏边的最后一张画", "你的外套"],
      open_loops: ["确认最后一张画上的人物是谁", "林晚还没有松开你的手"]
    },
    narration: "天台的风突然卷走一叠速写。你替林晚拦下最后一张，也在她靠近围栏时先一步拉住了她的手腕。那张画上，是一个和你侧脸很像的人。",
    opening: "画先还我，手可以晚一点再松。\n\n别这么看我，那张侧脸不是故意画成你的。至少……一开始不是。你要听真话，还是给我留点面子？",
    suggestions: ["手先不松，真话也要听", "你什么时候开始觉得那个人像我？"],
    icebreakers: ["我选真话", "这张画是不是画的我", "你先解释为什么不让我松手"]
  }
];

const CHARACTERS = [
  {
    id: "lin-wan", name: "林晚", gender: "female", age: 24, city: "成都", occupation: "自由插画师",
    archetype: "温柔慢热", intro: "温柔、细腻、有一点慢热。喜欢插画、晚风、猫和旧电影。",
    tags: ["慢热", "旧电影", "晚风"], accent: "#d85f6a", initial: "晚",
    values: ["真诚", "细致", "尊重自主"], likesInPeople: ["认真倾听", "记得小事", "坦率表达"], dislikesInPeople: ["敷衍", "替她做决定", "把脆弱当玩笑"],
    avatar: "assets/avatars/lin-wan-avatar.png?v=20260717.2",
    life: { current_goal: "完成一本城市散步主题小册子的插画样稿", current_problem: "其中一张夜景构图还没有找到满意的方向", next_plan: "周末去旧书店找城市照片和排版参考", recent_events: [] },
    scenarios: INITIAL_SCENARIOS
  },
  ...window.HEART_TALK_ADDITIONAL_CHARACTERS
];

const requestedCharacterId = localStorage.getItem(CHARACTER_SELECTION_KEY) || "lin-wan";
const ACTIVE_CHARACTER = CHARACTERS.find((character) => character.id === requestedCharacterId) || CHARACTERS[0];
const ACTIVE_SCENARIOS = ACTIVE_CHARACTER.scenarios;
const STORAGE_KEY = `${STORAGE_KEY_PREFIX}:${ACTIVE_CHARACTER.id}`;

function pickInitialScenario(scenarios) {
  const values = new Uint32Array(1);
  if (window.crypto && window.crypto.getRandomValues) window.crypto.getRandomValues(values);
  else values[0] = Math.floor(Math.random() * 0xffffffff);
  return scenarios[values[0] % scenarios.length];
}

const INITIAL_SCENARIO = pickInitialScenario(ACTIVE_SCENARIOS);

function initialArc(scenario) {
  return {
    phase: "试探",
    central_conflict: String(scenario.arc?.central_conflict || scenario.scene.open_loops?.[0] || "彼此仍在判断要不要继续靠近"),
    shared_goal: String(scenario.arc?.shared_goal || scenario.scene.open_loops?.[1] || "把当前事件处理清楚"),
    last_beat: String(scenario.arc?.last_beat || scenario.scene.activity || "故事刚刚开始"),
    tension: Number(scenario.arc?.tension ?? 45),
    trust: Number(scenario.arc?.trust ?? 15),
    resolved: false,
    started_at_turn: 0
  };
}

function createMemoryId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID().replaceAll("-", "");
  }
  const values = new Uint8Array(16);
  if (window.crypto && window.crypto.getRandomValues) window.crypto.getRandomValues(values);
  else values.forEach((_, index) => { values[index] = Math.floor(Math.random() * 256); });
  return [...values].map((value) => value.toString(16).padStart(2, "0")).join("");
}

const defaultState = {
  characterId: ACTIVE_CHARACTER.id,
  memoryId: createMemoryId(),
  scenarioId: INITIAL_SCENARIO.id,
  messages: [],
  turns: 0,
  affinity: 4,
  memories: [],
  topics: [],
  topicHistory: [],
  topicDomains: [],
  moveHistory: [],
  interactionPatterns: [],
  initiativeHistory: [],
  topicSourceHistory: [],
  storyBeats: [],
  replyOpenings: [],
  locationHistory: [INITIAL_SCENARIO.scene.location],
  matureMode: false,
  adultConfirmed: false,
  lastSuggestions: [],
  suggestionHistory: [],
  scene: {
    ...INITIAL_SCENARIO.scene,
    active_props: [...INITIAL_SCENARIO.scene.active_props],
    open_loops: [...INITIAL_SCENARIO.scene.open_loops],
    started_at_turn: 0
  },
  arc: initialArc(INITIAL_SCENARIO),
  life: { ...ACTIVE_CHARACTER.life, recent_events: [] }
};

const state = loadState();

function getScenario(id) {
  return ACTIVE_SCENARIOS.find((scenario) => scenario.id === id) || INITIAL_SCENARIO;
}

function setScenarioState(scenario) {
  state.scenarioId = scenario.id;
  state.scene = {
    ...scenario.scene,
    active_props: [...scenario.scene.active_props],
    open_loops: [...scenario.scene.open_loops],
    started_at_turn: 0
  };
  state.arc = initialArc(scenario);
}

function configureIcebreakers(scenario) {
  const buttons = [...document.querySelectorAll("[data-message]")];
  buttons.forEach((button, index) => {
    const message = scenario.icebreakers[index];
    if (!message) return;
    button.dataset.message = message;
    button.textContent = message;
  });
}

function renderCharacterAvatar(element, character) {
  if (!element) return;
  element.replaceChildren();
  if (character.avatar) {
    const image = document.createElement("img");
    image.src = character.avatar;
    image.alt = "";
    element.appendChild(image);
    element.classList.remove("initial-avatar");
  } else {
    element.textContent = character.initial;
    element.classList.add("initial-avatar");
    element.style.backgroundColor = character.accent;
  }
}

function renderCharacterProfile() {
  document.documentElement.style.setProperty("--character-accent", ACTIVE_CHARACTER.accent);
  elements.characterSelect.replaceChildren();
  CHARACTERS.forEach((character) => {
    const option = document.createElement("option");
    option.value = character.id;
    option.textContent = `${character.name} · ${character.archetype}`;
    option.selected = character.id === ACTIVE_CHARACTER.id;
    elements.characterSelect.appendChild(option);
  });
  elements.characterName.textContent = ACTIVE_CHARACTER.name;
  elements.companionName.textContent = ACTIVE_CHARACTER.name;
  elements.companionMeta.textContent = `${ACTIVE_CHARACTER.age} 岁 · ${ACTIVE_CHARACTER.city} · ${ACTIVE_CHARACTER.occupation}`;
  elements.companionPanel.setAttribute("aria-label", `${ACTIVE_CHARACTER.name}的人物状态`);
  elements.input.placeholder = `和${ACTIVE_CHARACTER.name}说点什么…`;
  elements.drawerEyebrow.textContent = ACTIVE_CHARACTER.gender === "male" ? "ABOUT HIM" : "ABOUT HER";
  elements.drawerTitle.textContent = `${ACTIVE_CHARACTER.name}的记忆`;
  elements.drawerProfileName.textContent = `${ACTIVE_CHARACTER.name} · ${ACTIVE_CHARACTER.age}岁`;
  elements.drawerProfileMeta.textContent = `${ACTIVE_CHARACTER.city} · ${ACTIVE_CHARACTER.occupation}`;
  elements.personaDescription.textContent = ACTIVE_CHARACTER.intro;
  elements.memoryOwnerLabel.textContent = `${ACTIVE_CHARACTER.gender === "male" ? "他" : "她"}记住的你`;
  elements.personaTags.replaceChildren();
  ACTIVE_CHARACTER.tags.forEach((tag) => {
    const item = document.createElement("span");
    item.textContent = tag;
    elements.personaTags.appendChild(item);
  });
  [elements.companionPortrait, elements.headerAvatar, elements.drawerAvatar].forEach((element) => {
    renderCharacterAvatar(element, ACTIVE_CHARACTER);
  });
}

function changeCharacter(event) {
  const characterId = String(event.target.value || "");
  if (!CHARACTERS.some((character) => character.id === characterId) || characterId === ACTIVE_CHARACTER.id) return;
  localStorage.setItem(CHARACTER_SELECTION_KEY, characterId);
  window.location.reload();
}

const elements = {
  messages: document.querySelector("#messages"),
  form: document.querySelector("#chatForm"),
  input: document.querySelector("#messageInput"),
  send: document.querySelector("#sendButton"),
  template: document.querySelector("#messageTemplate"),
  replyPanel: document.querySelector("#replyPanel"),
  optionA: document.querySelector("#optionA"),
  optionB: document.querySelector("#optionB"),
  turnCounter: document.querySelector("#turnCounter"),
  stageBadge: document.querySelector("#stageBadge"),
  progressBar: document.querySelector("#progressBar"),
  affinityFeedback: document.querySelector("#affinityFeedback"),
  relationshipText: document.querySelector("#relationshipText"),
  drawer: document.querySelector("#memoryDrawer"),
  backdrop: document.querySelector("#drawerBackdrop"),
  memoryList: document.querySelector("#memoryList"),
  topicChips: document.querySelector("#topicChips"),
  momentText: document.querySelector("#momentText"),
  lifeGoalText: document.querySelector("#lifeGoalText"),
  lifeProblemText: document.querySelector("#lifeProblemText"),
  lifePlanText: document.querySelector("#lifePlanText"),
  storyPhase: document.querySelector("#storyPhase"),
  storyConflict: document.querySelector("#storyConflict"),
  storyGoal: document.querySelector("#storyGoal"),
  trustBar: document.querySelector("#trustBar"),
  tensionBar: document.querySelector("#tensionBar"),
  matureModeToggle: document.querySelector("#matureModeToggle"),
  matureModeState: document.querySelector("#matureModeState"),
  icebreakers: document.querySelector("#icebreakers"),
  onlineText: document.querySelector(".online-text")
  ,characterSelect: document.querySelector("#characterSelect")
  ,characterName: document.querySelector("#characterName")
  ,companionPanel: document.querySelector("#companionPanel")
  ,companionPortrait: document.querySelector("#companionPortrait")
  ,companionName: document.querySelector("#companionName")
  ,companionMeta: document.querySelector("#companionMeta")
  ,personaTags: document.querySelector("#personaTags")
  ,headerAvatar: document.querySelector("#headerAvatar")
  ,drawerAvatar: document.querySelector("#drawerAvatar")
  ,drawerEyebrow: document.querySelector("#drawerEyebrow")
  ,drawerTitle: document.querySelector("#drawerTitle")
  ,drawerProfileName: document.querySelector("#drawerProfileName")
  ,drawerProfileMeta: document.querySelector("#drawerProfileMeta")
  ,personaDescription: document.querySelector("#personaDescription")
  ,memoryOwnerLabel: document.querySelector("#memoryOwnerLabel")
};

init();

async function init() {
  renderCharacterProfile();
  const scenario = getScenario(state.scenarioId);
  const hasLegacyOpening = state.turns === 0 && state.messages.some((message) => (
    String(message.text || "").includes("躲雨的橘猫") || String(message.text || "").includes("便利店出来")
  ));
  if (hasLegacyOpening) {
    state.messages = [];
    state.lastSuggestions = [];
    setScenarioState(scenario);
  }
  configureIcebreakers(scenario);

  if (state.messages.length === 0) {
    const now = Date.now();
    setScenarioState(scenario);
    addMessage("narration", scenario.narration, now - 18000);
    addMessage("assistant", scenario.opening, now);
    setSuggestions(scenario.suggestions);
  } else {
    state.messages.forEach(renderMessage);
    setSuggestions(state.lastSuggestions);
  }

  if (state.turns > 0) elements.icebreakers.hidden = true;
  updateStatus();
  renderCompanionState();
  renderMemory();
  renderMatureMode();
  bindEvents();
  requestAnimationFrame(scrollToBottom);
  await checkModelStatus();
}

function bindEvents() {
  elements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendCurrentMessage();
  });

  elements.input.addEventListener("input", autoResize);
  elements.input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendCurrentMessage();
    }
  });

  elements.optionA.addEventListener("click", () => chooseSuggestion(elements.optionA.textContent));
  elements.optionB.addEventListener("click", () => chooseSuggestion(elements.optionB.textContent));
  document.querySelectorAll("[data-message]").forEach((button) => {
    button.addEventListener("click", () => chooseSuggestion(button.dataset.message));
  });
  document.querySelector("#memoryButton").addEventListener("click", openDrawer);
  document.querySelector("#closeDrawer").addEventListener("click", closeDrawer);
  elements.backdrop.addEventListener("click", closeDrawer);
  document.querySelector("#resetButton").addEventListener("click", resetConversation);
  elements.matureModeToggle.addEventListener("change", handleMatureModeChange);
  elements.characterSelect.addEventListener("change", changeCharacter);
}

async function sendCurrentMessage() {
  const text = elements.input.value.trim();
  if (!text || elements.send.disabled) return;

  elements.input.value = "";
  autoResize();
  const pendingMessage = { role: "user", text, time: Date.now(), pending: true };
  state.messages.push(pendingMessage);
  saveState();
  renderMessage(pendingMessage);
  state.turns += 1;
  elements.replyPanel.hidden = true;
  elements.icebreakers.hidden = true;
  setBusy(true);
  updateStatus();

  const typing = showTyping();
  try {
    const result = await requestAIReply(text);
    typing.remove();

    if (result.user_message_type === "action" && result.user_action_narration) {
      convertLatestUserMessageToNarration(result.user_action_narration);
    }
    const latestUser = [...state.messages].reverse().find((message) => message.role === "user");
    if (latestUser) delete latestUser.pending;
    saveState();
    if (result.narration) addMessage("narration", result.narration);
    addMessage("assistant", result.reply);
    if (Array.isArray(result.stored_memories)) {
      state.memories = cleanStateList(result.stored_memories, 20);
      saveState();
    } else {
      mergeMemories(result.memory_updates);
    }
    applySceneUpdate(result.scene_update);
    applyLifeUpdate(result.life_update);
    applyAffinityUpdate(result.affinity_update);
    applyArcUpdate(result.arc_update);
    rememberTopic(
      result.topic,
      result.conversation_move,
      result.interaction_pattern,
      result.topic_domain,
      result.initiative,
      result.topic_source
    );
    setSuggestions(result.suggestions);
    renderMemory();
    elements.onlineText.textContent = "AI在线";
  } catch (error) {
    typing.remove();
    removePendingUserMessage();
    const backendOnline = await isBackendOnline();
    const onlineError = String(error && error.message || "").trim();
    addNotice(
      backendOnline ? (onlineError || "DeepSeek当前响应繁忙，已为你保留输入。") : "本地服务暂时不可用，已为你保留输入。",
      true
    );
    elements.input.value = text;
    autoResize();
    elements.onlineText.textContent = backendOnline ? "AI繁忙" : "未连接";
  } finally {
    setBusy(false);
    elements.input.focus();
  }
}

async function isBackendOnline() {
  try {
    const response = await fetch(`${API_ORIGIN}/api/status?_=${Date.now()}`, { cache: "no-store" });
    return response.ok;
  } catch {
    return false;
  }
}

function removePendingUserMessage() {
  const index = state.messages.findLastIndex
    ? state.messages.findLastIndex((message) => message.role === "user" && message.pending)
    : state.messages.map((message) => message.role === "user" && message.pending).lastIndexOf(true);
  if (index >= 0) {
    state.messages.splice(index, 1);
    state.turns = Math.max(0, state.turns - 1);
    saveState();
    elements.messages.innerHTML = "";
    state.messages.forEach(renderMessage);
    updateStatus();
  }
}

function convertLatestUserMessageToNarration(text) {
  for (let index = state.messages.length - 1; index >= 0; index -= 1) {
    if (state.messages[index].role === "user") {
      state.messages[index].role = "narration";
      state.messages[index].text = text;
      saveState();
      elements.messages.innerHTML = "";
      state.messages.forEach(renderMessage);
      requestAnimationFrame(scrollToBottom);
      return;
    }
  }
}

async function requestAIReply(latestMessage) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 45000);
  let response;
  try {
    response = await fetch(`${API_ORIGIN}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({
      latest_message: latestMessage,
      character_id: ACTIVE_CHARACTER.id,
      memory_id: state.memoryId,
      relationship: getStage(),
      turns: state.turns,
      memories: state.memories,
      topics: state.topics,
      recent_topics: state.topicHistory.slice(-60),
      recent_topic_domains: state.topicDomains.slice(-32),
      recent_moves: state.moveHistory.slice(-40),
      recent_patterns: state.interactionPatterns.slice(-20),
      recent_initiatives: state.initiativeHistory.slice(-20),
      recent_topic_sources: state.topicSourceHistory.slice(-24),
      recent_story_beats: state.storyBeats.slice(-32),
      recent_reply_openings: state.replyOpenings.slice(-80),
      recent_locations: state.locationHistory.slice(-10),
      recent_suggestions: state.suggestionHistory.slice(-60),
      scenario_id: state.scenarioId,
      mature_mode: state.matureMode === true,
      adult_confirmed: state.adultConfirmed === true,
      scene: getSceneContext(),
      scene_age_turns: Math.max(0, state.turns - Number(state.scene.started_at_turn || 0)),
      arc: state.arc,
      life: state.life,
      messages: state.messages
        .filter((message) => message.role === "user" || message.role === "assistant" || message.role === "narration")
        .slice(-40)
        .map(({ role, text }) => ({ role, text }))
      })
    });
  } catch (error) {
    if (error.name === "AbortError") throw new Error("回复等待超时，请重新发送。");
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "模型请求失败，请检查后端配置。");
  }
  if (!payload.reply || !Array.isArray(payload.suggestions) || payload.suggestions.length < 2) {
    throw new Error("模型返回的数据不完整，请重新发送一次。");
  }
  return payload;
}

async function checkModelStatus() {
  try {
    const response = await fetch(`${API_ORIGIN}/api/status?_=${Date.now()}`, { cache: "no-store" });
    const status = await response.json();
    if (status.configured) {
      elements.onlineText.textContent = "AI在线";
      elements.onlineText.title = `当前模型：${status.model}`;
    } else {
      elements.onlineText.textContent = "待配置";
      elements.onlineText.title = "请先在 .env 中配置 AI_API_KEY";
    }
  } catch {
    elements.onlineText.textContent = "需启动后端";
    elements.onlineText.title = "请运行 python server.py，不要直接双击网页";
  }
}

function addMessage(role, text, time = Date.now()) {
  if (role === "narration") {
    const clean = String(text || "").trim();
    const duplicate = state.messages.slice(-12).some((message) => (
      message.role === "narration" && String(message.text || "").trim() === clean
    ));
    if (!clean || duplicate) return;
    const previous = state.messages[state.messages.length - 1];
    if (previous && previous.role === "narration") {
      previous.text = `${String(previous.text || "").trim()} ${clean}`.trim();
      saveState();
      elements.messages.innerHTML = "";
      state.messages.forEach(renderMessage);
      requestAnimationFrame(scrollToBottom);
      return;
    }
  }
  const message = { role, text, time };
  state.messages.push(message);
  if (role === "assistant") {
    const opening = String(text || "").replace(/\s+/g, " ").trim().slice(0, 28);
    if (opening) {
      state.replyOpenings = [...(state.replyOpenings || []), opening].slice(-100);
    }
  }
  if (state.messages.length > 220) state.messages = state.messages.slice(-220);
  saveState();
  renderMessage(message);
  requestAnimationFrame(scrollToBottom);
}

function renderMessage(message) {
  if (message.role === "narration") {
    const clean = String(message.text || "").trim();
    const recentNarrations = [...elements.messages.querySelectorAll(".narration-row p")].slice(-12);
    if (!clean || recentNarrations.some((item) => item.textContent.trim() === clean)) return;
    const previousNarration = elements.messages.lastElementChild;
    if (previousNarration && previousNarration.classList.contains("narration-row")) {
      const paragraph = previousNarration.querySelector("p");
      paragraph.textContent = `${paragraph.textContent.trim()} ${clean}`;
      return;
    }
    const narration = document.createElement("div");
    narration.className = "narration-row";
    narration.innerHTML = "<span>场景</span><p></p>";
    narration.querySelector("p").textContent = message.text;
    elements.messages.appendChild(narration);
    return;
  }

  const fragment = elements.template.content.cloneNode(true);
  const row = fragment.querySelector(".message-row");
  const avatar = fragment.querySelector(".avatar");
  row.classList.add(message.role);
  if (message.role === "user") avatar.textContent = "你";
  else renderCharacterAvatar(avatar, ACTIVE_CHARACTER);
  fragment.querySelector(".bubble").textContent = message.text;
  fragment.querySelector("time").textContent = formatTime(message.time);
  elements.messages.appendChild(fragment);
}

function addNotice(text, retryable = false) {
  const notice = document.createElement("div");
  notice.className = "system-notice";
  notice.innerHTML = "<strong>暂时没能收到回复</strong><p></p>";
  notice.querySelector("p").textContent = text;
  if (retryable) {
    const retry = document.createElement("button");
    retry.type = "button";
    retry.className = "retry-button";
    retry.textContent = "重新发送";
    retry.addEventListener("click", () => {
      notice.remove();
      sendCurrentMessage();
    });
    notice.appendChild(retry);
  }
  elements.messages.appendChild(notice);
  scrollToBottom();
}

function showTyping() {
  const row = document.createElement("article");
  row.className = "message-row assistant typing";
  row.innerHTML = '<div class="avatar character-avatar"></div><div class="message-content"><div class="bubble"><i></i><i></i><i></i></div></div>';
  renderCharacterAvatar(row.querySelector(".avatar"), ACTIVE_CHARACTER);
  elements.messages.appendChild(row);
  scrollToBottom();
  return row;
}

function setSuggestions(suggestions) {
  if (!Array.isArray(suggestions) || suggestions.length < 2) {
    elements.replyPanel.hidden = true;
    return;
  }
  const clean = suggestions.slice(0, 2).map((item) => String(item).trim()).filter(Boolean);
  if (clean.length < 2) {
    elements.replyPanel.hidden = true;
    return;
  }
  state.lastSuggestions = clean;
  clean.forEach((item) => {
    if (!state.suggestionHistory.includes(item)) state.suggestionHistory.push(item);
  });
  state.suggestionHistory = state.suggestionHistory.slice(-100);
  elements.optionA.textContent = clean[0];
  elements.optionB.textContent = clean[1];
  elements.replyPanel.hidden = false;
  saveState();
  requestAnimationFrame(scrollToBottom);
}

function chooseSuggestion(text) {
  elements.input.value = text;
  autoResize();
  sendCurrentMessage();
}

function mergeMemories(updates) {
  if (!Array.isArray(updates)) return;
  updates.forEach((memory) => {
    if (memory && typeof memory === "object" && memory.action === "forget") return;
    const clean = String(memory && typeof memory === "object" ? memory.content : memory).trim();
    if (clean && !state.memories.includes(clean)) state.memories.push(clean);
  });
  state.memories = state.memories.slice(-20);
  saveState();
}

function cleanStateList(items, limit = 8) {
  if (!Array.isArray(items)) return [];
  return [...new Set(items.map((item) => String(item || "").trim()).filter(Boolean))].slice(-limit);
}

function getSceneContext() {
  return {
    location: String(state.scene.location || ""),
    time: String(state.scene.time || ""),
    activity: String(state.scene.activity || ""),
    active_props: cleanStateList(state.scene.active_props),
    open_loops: cleanStateList(state.scene.open_loops)
  };
}

function removeMatchingItems(items, removals) {
  const cleanRemovals = cleanStateList(removals);
  return cleanStateList(items).filter((item) => (
    !cleanRemovals.some((removal) => item === removal || item.includes(removal) || removal.includes(item))
  ));
}

function applySceneUpdate(update) {
  if (!update || typeof update !== "object") return;
  let changed = false;
  let locationChanged = false;
  ["location", "time", "activity"].forEach((key) => {
    const value = String(update[key] || "").trim();
    if (value && value !== state.scene[key]) {
      state.scene[key] = value;
      changed = true;
      if (key === "location") {
        locationChanged = true;
        state.locationHistory.push(value);
        state.locationHistory = cleanStateList(state.locationHistory, 12);
      }
    }
  });

  const remainingProps = removeMatchingItems(state.scene.active_props, update.remove_props);
  const nextProps = cleanStateList([...remainingProps, ...cleanStateList(update.add_props)]);
  const remainingLoops = removeMatchingItems(state.scene.open_loops, update.close_open_loops);
  const nextLoops = cleanStateList([...remainingLoops, ...cleanStateList(update.add_open_loops)]);
  if (JSON.stringify(nextProps) !== JSON.stringify(state.scene.active_props)) changed = true;
  if (JSON.stringify(nextLoops) !== JSON.stringify(state.scene.open_loops)) changed = true;
  state.scene.active_props = nextProps;
  state.scene.open_loops = nextLoops;
  if (locationChanged) state.scene.started_at_turn = state.turns;
  saveState();
  renderCompanionState();
}

function applyLifeUpdate(update) {
  if (!update || typeof update !== "object") return;
  ["current_goal", "current_problem", "next_plan"].forEach((key) => {
    const value = String(update[key] || "").trim();
    if (value) state.life[key] = value;
  });
  const recentEvent = String(update.recent_event || "").trim();
  if (recentEvent) {
    state.life.recent_events = cleanStateList([...state.life.recent_events, recentEvent], 6);
  }
  saveState();
  renderCompanionState();
}

function applyArcUpdate(update) {
  if (!update || typeof update !== "object") return;
  const previousConflict = String(state.arc.central_conflict || "");
  const phases = ["对峙", "试探", "松动", "信任", "暧昧", "确认"];
  const phase = String(update.phase || "").trim();
  if (phases.includes(phase)) state.arc.phase = phase;
  ["central_conflict", "shared_goal", "last_beat"].forEach((key) => {
    const value = String(update[key] || "").trim();
    if (value) state.arc[key] = value;
  });
  if (update.central_conflict && String(update.central_conflict).trim() !== previousConflict) {
    state.arc.resolved = false;
    state.arc.started_at_turn = state.turns;
  }
  const tensionDelta = Math.max(-12, Math.min(12, Number(update.tension_delta || 0)));
  const trustDelta = Math.max(-8, Math.min(8, Number(update.trust_delta || 0)));
  state.arc.tension = Math.max(0, Math.min(100, Number(state.arc.tension || 0) + tensionDelta));
  state.arc.trust = Math.max(0, Math.min(100, Number(state.arc.trust || 0) + trustDelta));
  if (update.resolved === true && ["对峙", "试探"].includes(state.arc.phase)) state.arc.phase = "松动";
  if (update.resolved === true) state.arc.resolved = true;
  if (state.arc.last_beat) {
    state.storyBeats = [...(state.storyBeats || []), state.arc.last_beat].slice(-80);
  }
  saveState();
  renderCompanionState();
}

function renderCompanionState() {
  const sceneParts = [state.scene.time, state.scene.activity, state.scene.location]
    .map((item) => String(item || "").trim())
    .filter((item, index, items) => item && items.indexOf(item) === index);
  if (elements.momentText) elements.momentText.textContent = sceneParts.join(" · ") || "正在和你聊天";
  if (elements.lifeGoalText) elements.lifeGoalText.textContent = state.life.current_goal || "慢慢完成手上的画";
  if (elements.lifeProblemText) elements.lifeProblemText.textContent = state.life.current_problem || "最近没有特别棘手的事。";
  if (elements.lifePlanText) elements.lifePlanText.textContent = state.life.next_plan || "给自己留一点散步的时间。";
  if (elements.storyPhase) elements.storyPhase.textContent = state.arc.phase || "试探";
  if (elements.storyConflict) elements.storyConflict.textContent = state.arc.central_conflict || "彼此仍在判断要不要继续靠近";
  if (elements.storyGoal) elements.storyGoal.textContent = `共同目标：${state.arc.shared_goal || "把当前事件处理清楚"}`;
  if (elements.trustBar) elements.trustBar.style.width = `${Math.max(3, Number(state.arc.trust || 0))}%`;
  if (elements.tensionBar) elements.tensionBar.style.width = `${Math.max(3, Number(state.arc.tension || 0))}%`;
}

function rememberTopic(topic, move, pattern, domain, initiative, source) {
  const clean = String(topic || "").trim();
  if (clean) {
    state.topics = state.topics.filter((item) => item !== clean);
    state.topics.push(clean);
    state.topics = state.topics.slice(-8);
    state.topicHistory.push(clean);
    state.topicHistory = state.topicHistory.slice(-80);
  }
  const cleanMove = String(move || "").trim();
  if (cleanMove) {
    state.moveHistory.push(cleanMove);
    state.moveHistory = state.moveHistory.slice(-60);
  }
  const cleanPattern = String(pattern || "").trim();
  if (cleanPattern) {
    state.interactionPatterns.push(cleanPattern);
    state.interactionPatterns = state.interactionPatterns.slice(-40);
  }
  const cleanDomain = String(domain || "").trim();
  if (cleanDomain) {
    state.topicDomains.push(cleanDomain);
    state.topicDomains = state.topicDomains.slice(-50);
  }
  const cleanInitiative = String(initiative || "").trim();
  if (cleanInitiative) {
    state.initiativeHistory.push(cleanInitiative);
    state.initiativeHistory = state.initiativeHistory.slice(-40);
  }
  const cleanSource = String(source || "").trim();
  if (cleanSource) {
    state.topicSourceHistory.push(cleanSource);
    state.topicSourceHistory = state.topicSourceHistory.slice(-60);
  }
  saveState();
}

function handleMatureModeChange() {
  if (elements.matureModeToggle.checked && !state.adultConfirmed) {
    const confirmed = window.confirm(
      "请确认你已年满18岁。该模式会增强成年人之间的暧昧、身体距离和亲密暗示，但不会生成图解式性行为描写。"
    );
    if (!confirmed) {
      elements.matureModeToggle.checked = false;
      renderMatureMode();
      return;
    }
    state.adultConfirmed = true;
  }
  state.matureMode = elements.matureModeToggle.checked && state.adultConfirmed;
  saveState();
  renderMatureMode();
}

function renderMatureMode() {
  if (!elements.matureModeToggle || !elements.matureModeState) return;
  const enabled = state.matureMode === true && state.adultConfirmed === true;
  elements.matureModeToggle.checked = enabled;
  elements.matureModeState.textContent = enabled ? "已开启 · 仅限成年人" : "未开启";
}

function applyAffinityUpdate(update) {
  if (!update || typeof update !== "object") return;
  const delta = Math.max(-8, Math.min(6, Math.trunc(Number(update.delta || 0))));
  state.affinity = Math.max(0, Math.min(100, Number(state.affinity || 0) + delta));
  saveState();
  updateStatus();
  if (!elements.affinityFeedback || delta === 0) return;
  const trigger = String(update.trigger || update.reaction || "关系变化").trim();
  elements.affinityFeedback.textContent = `${delta > 0 ? "+" : ""}${delta} · ${trigger}`;
  elements.affinityFeedback.className = delta > 0 ? "positive visible" : "negative visible";
  window.clearTimeout(applyAffinityUpdate.hideTimer);
  applyAffinityUpdate.hideTimer = window.setTimeout(() => {
    elements.affinityFeedback.classList.remove("visible");
  }, 2600);
}

function getStage() {
  const score = Math.max(0, Math.min(100, Number(state.affinity || 0)));
  const affinityLevel = score >= 72 ? 4 : score >= 48 ? 3 : score >= 27 ? 2 : score >= 10 ? 1 : 0;
  const phaseCaps = { "对峙": 1, "试探": 2, "松动": 2, "信任": 3, "暧昧": 4, "确认": 4 };
  const level = Math.min(affinityLevel, phaseCaps[state.arc?.phase] ?? 1);
  const stages = [
    { level: 0, name: "初识", copy: "刚刚认识 · 仍在判断彼此" },
    { level: 1, name: "了解", copy: "继续了解 · 好感也会有起伏" },
    { level: 2, name: "熟悉", copy: "渐渐熟悉 · 开始建立信任" },
    { level: 3, name: "心动", copy: "悄悄靠近 · 对彼此有了期待" },
    { level: 4, name: "亲密", copy: "彼此在意 · 分享更真实的心事" }
  ];
  return stages[level];
}

function updateStatus() {
  const stage = getStage();
  elements.turnCounter.textContent = `${state.turns} / 100 轮`;
  elements.stageBadge.textContent = stage.name;
  elements.relationshipText.textContent = stage.copy;
  elements.progressBar.style.width = `${Math.max(3, Math.min(100, Number(state.affinity || 0)))}%`;
  saveState();
}

function renderMemory() {
  elements.memoryList.innerHTML = "";
  const subject = ACTIVE_CHARACTER.gender === "male" ? "他" : "她";
  const memories = state.memories.length ? state.memories : [`聊得更多以后，${subject}会在这里记住关于你的小事`];
  memories.forEach((memory) => {
    const li = document.createElement("li");
    li.textContent = memory;
    if (!state.memories.length) li.className = "empty-memory";
    elements.memoryList.appendChild(li);
  });

  elements.topicChips.innerHTML = "";
  const topics = state.topics.length ? state.topics : ["等待第一次聊天"];
  topics.forEach((topic) => {
    const chip = document.createElement("span");
    chip.textContent = topic;
    elements.topicChips.appendChild(chip);
  });
}

function openDrawer() {
  renderMemory();
  renderMatureMode();
  elements.backdrop.hidden = false;
  elements.drawer.setAttribute("aria-hidden", "false");
  requestAnimationFrame(() => elements.drawer.classList.add("open"));
}

function closeDrawer() {
  elements.drawer.classList.remove("open");
  elements.drawer.setAttribute("aria-hidden", "true");
  window.setTimeout(() => { elements.backdrop.hidden = true; }, 300);
}

function resetConversation() {
  if (!window.confirm("确定清空聊天记录和记忆，重新开始吗？")) return;
  localStorage.removeItem(STORAGE_KEY);
  window.location.reload();
}

function setBusy(busy) {
  elements.send.disabled = busy;
  elements.input.disabled = busy;
}

function autoResize() {
  elements.input.style.height = "auto";
  elements.input.style.height = `${Math.min(elements.input.scrollHeight, 100)}px`;
}

function scrollToBottom() {
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

function formatTime(timestamp) {
  return new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(timestamp));
}

function replacePersonPronoun(value, pronoun, replacement) {
  const text = String(value || "");
  if (pronoun === "他") return text.replace(/(^|[^其])他/g, (_, prefix) => `${prefix}${replacement}`);
  return text.replaceAll(pronoun, replacement);
}

function migrateStoredMessages(messages) {
  if (!Array.isArray(messages)) return [];
  const migrated = [];
  const characterName = ACTIVE_CHARACTER.name;
  const characterPronoun = ACTIVE_CHARACTER.gender === "male" ? "他" : "她";
  const userPronoun = ACTIVE_CHARACTER.gender === "male" ? "她" : "他";
  const userAction = new RegExp(`^(?:我|你)?(?:[（(]|握住|牵住|拉住|抱住|靠近|凑近|凑过去|凑到|递给|抬手|低头|亲吻|搂住|推开|看着${characterPronoun}|走向${characterPronoun}|走过去|坐到|站到|看屏幕|指向|问${characterPronoun}|告诉${characterPronoun}|对${characterPronoun}说)`);
  const assistantAction = "(?:伸手|抬手|指指|指了指|指向|低头|侧身|起身|站起|坐下|走向|靠近|凑近|握住|牵住|吻|笑着|看着|望着|转身|递给|拿起|放下|晃了晃|歪头)";
  const quotedAction = new RegExp(`^(我${assistantAction}[^：:\\n]{0,60})[：:]\\s*[“\"‘'](.+?)[”\"’']?\\s*$`, "s");
  const sentenceAction = new RegExp(`^(我${assistantAction}[^。！？\\n]{0,60})[。！？]\\s*(.+)$`, "s");

  messages.forEach((message) => {
    if (!message || typeof message !== "object") return;
    const text = String(message.text || "").trim();
    if (message.role === "user" && userAction.test(text)) {
      let narration = text.replace(/[（）()]/g, "").replace(/^我/, "");
      narration = replacePersonPronoun(narration, characterPronoun, characterName);
      narration = replacePersonPronoun(narration, userPronoun, characterName);
      migrated.push({ ...message, role: "narration", text: `你${narration.replace(/[。！？!?]+$/, "")}。` });
      return;
    }
    if (message.role === "assistant") {
      const parenthetical = text.match(/^\s*[（(]([^）)]+)[）)]\s*(.+)$/s);
      const match = text.match(quotedAction) || text.match(sentenceAction);
      if (parenthetical) {
        const actorPattern = new RegExp(`^(?:${characterName}|${characterPronoun}|我)`);
        const action = actorPattern.test(parenthetical[1]) ? parenthetical[1] : `${characterName}${parenthetical[1]}`;
        let normalizedAction = action.replace(new RegExp(`^(?:${characterPronoun}|我)`), characterName);
        normalizedAction = replacePersonPronoun(normalizedAction, userPronoun, "你");
        migrated.push({ role: "narration", text: `${normalizedAction.replace(/[。！？]+$/, "")}。`, time: Number(message.time || Date.now()) - 1 });
        migrated.push({ ...message, text: parenthetical[2].trim() });
        return;
      }
      if (match) {
        migrated.push({ role: "narration", text: `${match[1].replace(/^我/, characterName).replace(/[。！？]+$/, "")}。`, time: Number(message.time || Date.now()) - 1 });
        migrated.push({ ...message, text: match[2].trim().replace(/^[“\"‘']|[”\"’']$/g, "") });
        return;
      }
    }
    if (message.role === "narration") {
      let narration = replacePersonPronoun(text, characterPronoun, characterName);
      narration = replacePersonPronoun(narration, userPronoun, "你");
      migrated.push({ ...message, text: narration });
      return;
    }
    migrated.push(message);
  });
  return migrated;
}

function loadState() {
  try {
    const serialized = localStorage.getItem(STORAGE_KEY)
      || (ACTIVE_CHARACTER.id === "lin-wan" ? localStorage.getItem(LEGACY_STORAGE_KEY) : null);
    const saved = JSON.parse(serialized);
    const loaded = saved && typeof saved === "object" ? { ...defaultState, ...saved } : { ...defaultState };
    const savedScene = saved && typeof saved.scene === "object" ? saved.scene : {};
    const savedLife = saved && typeof saved.life === "object" ? saved.life : {};
    const savedArc = saved && typeof saved.arc === "object" ? saved.arc : {};
    loaded.scene = {
      ...defaultState.scene,
      ...savedScene,
      active_props: cleanStateList(savedScene.active_props || defaultState.scene.active_props),
      open_loops: cleanStateList(savedScene.open_loops || defaultState.scene.open_loops)
    };
    loaded.life = {
      ...defaultState.life,
      ...savedLife,
      recent_events: cleanStateList(savedLife.recent_events || defaultState.life.recent_events, 6)
    };
    loaded.arc = {
      ...initialArc(getScenario(loaded.scenarioId)),
      ...savedArc,
      tension: Math.max(0, Math.min(100, Number(savedArc.tension ?? initialArc(getScenario(loaded.scenarioId)).tension))),
      trust: Math.max(0, Math.min(100, Number(savedArc.trust ?? initialArc(getScenario(loaded.scenarioId)).trust)))
    };
    loaded.affinity = Math.max(0, Math.min(100, Number(loaded.affinity ?? defaultState.affinity)));
    loaded.interactionPatterns = Array.isArray(loaded.interactionPatterns) ? loaded.interactionPatterns : [];
    loaded.topicDomains = Array.isArray(loaded.topicDomains) ? loaded.topicDomains : [];
    loaded.initiativeHistory = Array.isArray(loaded.initiativeHistory) ? loaded.initiativeHistory : [];
    loaded.topicSourceHistory = Array.isArray(loaded.topicSourceHistory) ? loaded.topicSourceHistory : [];
    loaded.storyBeats = Array.isArray(loaded.storyBeats) ? loaded.storyBeats.slice(-80) : [];
    loaded.replyOpenings = Array.isArray(loaded.replyOpenings) ? loaded.replyOpenings.slice(-100) : [];
    loaded.locationHistory = Array.isArray(loaded.locationHistory)
      ? cleanStateList(loaded.locationHistory, 12)
      : cleanStateList([loaded.scene.location], 12);
    loaded.adultConfirmed = loaded.adultConfirmed === true;
    loaded.matureMode = loaded.matureMode === true && loaded.adultConfirmed;
    loaded.characterId = ACTIVE_CHARACTER.id;
    loaded.memoryId = /^[a-f0-9]{32}$/i.test(String(loaded.memoryId || ""))
      ? String(loaded.memoryId).toLowerCase()
      : createMemoryId();
    loaded.memories = cleanStateList(loaded.memories, 20);
    loaded.messages = migrateStoredMessages(loaded.messages);
    return loaded;
  } catch {
    return {
      ...defaultState,
      scene: { ...defaultState.scene, active_props: [...defaultState.scene.active_props], open_loops: [] },
      life: { ...defaultState.life, recent_events: [] }
    };
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}
