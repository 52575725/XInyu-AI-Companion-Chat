"use strict";

const STORAGE_KEY = "heart-talk-ai-v1";
const API_ORIGIN = window.location.origin;

const INITIAL_SCENARIOS = [
  {
    id: "gallery-misunderstanding",
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

function pickInitialScenario() {
  const values = new Uint32Array(1);
  if (window.crypto && window.crypto.getRandomValues) window.crypto.getRandomValues(values);
  else values[0] = Math.floor(Math.random() * 0xffffffff);
  return INITIAL_SCENARIOS[values[0] % INITIAL_SCENARIOS.length];
}

const INITIAL_SCENARIO = pickInitialScenario();

const defaultState = {
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
  life: {
    current_goal: "完成一本城市散步主题小册子的插画样稿",
    current_problem: "其中一张夜景构图还没有找到满意的方向",
    next_plan: "周末去旧书店找城市照片和排版参考",
    recent_events: []
  }
};

const state = loadState();

function getScenario(id) {
  return INITIAL_SCENARIOS.find((scenario) => scenario.id === id) || INITIAL_SCENARIO;
}

function setScenarioState(scenario) {
  state.scenarioId = scenario.id;
  state.scene = {
    ...scenario.scene,
    active_props: [...scenario.scene.active_props],
    open_loops: [...scenario.scene.open_loops],
    started_at_turn: 0
  };
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
  relationshipText: document.querySelector("#relationshipText"),
  drawer: document.querySelector("#memoryDrawer"),
  backdrop: document.querySelector("#drawerBackdrop"),
  memoryList: document.querySelector("#memoryList"),
  topicChips: document.querySelector("#topicChips"),
  momentText: document.querySelector("#momentText"),
  lifeGoalText: document.querySelector("#lifeGoalText"),
  lifeProblemText: document.querySelector("#lifeProblemText"),
  lifePlanText: document.querySelector("#lifePlanText"),
  matureModeToggle: document.querySelector("#matureModeToggle"),
  matureModeState: document.querySelector("#matureModeState"),
  icebreakers: document.querySelector("#icebreakers"),
  onlineText: document.querySelector(".online-text")
};

init();

async function init() {
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
  state.affinity = Math.min(100, state.affinity + affinityGain(text));
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
    mergeMemories(result.memory_updates);
    applySceneUpdate(result.scene_update);
    applyLifeUpdate(result.life_update);
    rememberTopic(
      result.topic,
      result.conversation_move,
      result.interaction_pattern,
      result.topic_domain,
      result.initiative
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
      relationship: getStage(),
      turns: state.turns,
      memories: state.memories,
      topics: state.topics,
      recent_topics: state.topicHistory.slice(-16),
      recent_topic_domains: state.topicDomains.slice(-12),
      recent_moves: state.moveHistory.slice(-12),
      recent_patterns: state.interactionPatterns.slice(-8),
      recent_initiatives: state.initiativeHistory.slice(-8),
      recent_locations: state.locationHistory.slice(-10),
      recent_suggestions: state.suggestionHistory.slice(-12),
      scenario_id: state.scenarioId,
      mature_mode: state.matureMode === true,
      adult_confirmed: state.adultConfirmed === true,
      scene: getSceneContext(),
      scene_age_turns: Math.max(0, state.turns - Number(state.scene.started_at_turn || 0)),
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
  row.innerHTML = '<div class="avatar"><img src="assets/avatars/lin-wan-avatar.png?v=20260716.4" alt=""></div><div class="message-content"><div class="bubble"><i></i><i></i><i></i></div></div>';
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
  state.suggestionHistory = state.suggestionHistory.slice(-30);
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
    const clean = String(memory).trim();
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

function renderCompanionState() {
  const sceneParts = [state.scene.time, state.scene.activity, state.scene.location]
    .map((item) => String(item || "").trim())
    .filter((item, index, items) => item && items.indexOf(item) === index);
  if (elements.momentText) elements.momentText.textContent = sceneParts.join(" · ") || "正在和你聊天";
  if (elements.lifeGoalText) elements.lifeGoalText.textContent = state.life.current_goal || "慢慢完成手上的画";
  if (elements.lifeProblemText) elements.lifeProblemText.textContent = state.life.current_problem || "最近没有特别棘手的事。";
  if (elements.lifePlanText) elements.lifePlanText.textContent = state.life.next_plan || "给自己留一点散步的时间。";
}

function rememberTopic(topic, move, pattern, domain, initiative) {
  const clean = String(topic || "").trim();
  if (clean) {
    state.topics = state.topics.filter((item) => item !== clean);
    state.topics.push(clean);
    state.topics = state.topics.slice(-8);
    state.topicHistory.push(clean);
    state.topicHistory = state.topicHistory.slice(-24);
  }
  const cleanMove = String(move || "").trim();
  if (cleanMove) {
    state.moveHistory.push(cleanMove);
    state.moveHistory = state.moveHistory.slice(-20);
  }
  const cleanPattern = String(pattern || "").trim();
  if (cleanPattern) {
    state.interactionPatterns.push(cleanPattern);
    state.interactionPatterns = state.interactionPatterns.slice(-16);
  }
  const cleanDomain = String(domain || "").trim();
  if (cleanDomain) {
    state.topicDomains.push(cleanDomain);
    state.topicDomains = state.topicDomains.slice(-20);
  }
  const cleanInitiative = String(initiative || "").trim();
  if (cleanInitiative) {
    state.initiativeHistory.push(cleanInitiative);
    state.initiativeHistory = state.initiativeHistory.slice(-16);
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

function affinityGain(text) {
  let gain = 1.4;
  if (text.length > 18) gain += 0.8;
  if (/谢谢|理解|关心|喜欢|想你|晚安|开心/.test(text)) gain += 1.2;
  return gain;
}

function getStage() {
  const score = Math.min(state.affinity, state.turns * 2 + 4);
  if (score >= 72 && state.turns >= 30) return { level: 4, name: "亲密", copy: "彼此在意 · 分享更真实的心事" };
  if (score >= 48 && state.turns >= 18) return { level: 3, name: "心动", copy: "悄悄靠近 · 对彼此有了期待" };
  if (score >= 27 && state.turns >= 9) return { level: 2, name: "熟悉", copy: "渐渐熟悉 · 记住彼此的小事" };
  if (state.turns >= 3) return { level: 1, name: "了解", copy: "继续了解 · 话题慢慢变多" };
  return { level: 0, name: "初识", copy: "刚刚认识 · 慢慢了解彼此" };
}

function updateStatus() {
  const stage = getStage();
  elements.turnCounter.textContent = `${state.turns} / 100 轮`;
  elements.stageBadge.textContent = stage.name;
  elements.relationshipText.textContent = stage.copy;
  elements.progressBar.style.width = `${Math.max(3, Math.min(100, state.turns))}%`;
  saveState();
}

function renderMemory() {
  elements.memoryList.innerHTML = "";
  const memories = state.memories.length ? state.memories : ["聊得更多以后，她会在这里记住关于你的小事"];
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

function migrateStoredMessages(messages) {
  if (!Array.isArray(messages)) return [];
  const migrated = [];
  const userAction = /^(?:我|你)?(?:[（(]|握住|牵住|拉住|抱住|靠近|凑近|凑过去|凑到|递给|抬手|低头|亲吻|搂住|推开|看着她|走向她|走过去|坐到|站到|看屏幕|指向|问她|告诉她|对她说)/;
  const assistantAction = "(?:伸手|抬手|指指|指了指|指向|低头|侧身|起身|站起|坐下|走向|靠近|凑近|握住|牵住|吻|笑着|看着|望着|转身|递给|拿起|放下|晃了晃|歪头)";
  const quotedAction = new RegExp(`^(我${assistantAction}[^：:\\n]{0,60})[：:]\\s*[“\"‘'](.+?)[”\"’']?\\s*$`, "s");
  const sentenceAction = new RegExp(`^(我${assistantAction}[^。！？\\n]{0,60})[。！？]\\s*(.+)$`, "s");

  messages.forEach((message) => {
    if (!message || typeof message !== "object") return;
    const text = String(message.text || "").trim();
    if (message.role === "user" && userAction.test(text)) {
      const narration = text.replace(/[（）()]/g, "").replace(/^我/, "").replaceAll("她", "林晚").replace(/他(?=的|[，。！？、]|$)/g, "林晚");
      migrated.push({ ...message, role: "narration", text: `你${narration.replace(/[。！？!?]+$/, "")}。` });
      return;
    }
    if (message.role === "assistant") {
      const parenthetical = text.match(/^\s*[（(]([^）)]+)[）)]\s*(.+)$/s);
      const match = text.match(quotedAction) || text.match(sentenceAction);
      if (parenthetical) {
        const action = /^(?:林晚|她|我)/.test(parenthetical[1]) ? parenthetical[1] : `林晚${parenthetical[1]}`;
        migrated.push({ role: "narration", text: `${action.replace(/^(?:她|我)/, "林晚").replace(/他(?=的|[，。！？、]|$)/g, "你").replace(/[。！？]+$/, "")}。`, time: Number(message.time || Date.now()) - 1 });
        migrated.push({ ...message, text: parenthetical[2].trim() });
        return;
      }
      if (match) {
        migrated.push({ role: "narration", text: `${match[1].replace(/^我/, "林晚").replace(/[。！？]+$/, "")}。`, time: Number(message.time || Date.now()) - 1 });
        migrated.push({ ...message, text: match[2].trim().replace(/^[“\"‘']|[”\"’']$/g, "") });
        return;
      }
    }
    if (message.role === "narration") {
      migrated.push({ ...message, text: text.replaceAll("她", "林晚").replace(/他(?=的|[，。！？、]|$)/g, "你") });
      return;
    }
    migrated.push(message);
  });
  return migrated;
}

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    const loaded = saved && typeof saved === "object" ? { ...defaultState, ...saved } : { ...defaultState };
    const savedScene = saved && typeof saved.scene === "object" ? saved.scene : {};
    const savedLife = saved && typeof saved.life === "object" ? saved.life : {};
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
    loaded.interactionPatterns = Array.isArray(loaded.interactionPatterns) ? loaded.interactionPatterns : [];
    loaded.topicDomains = Array.isArray(loaded.topicDomains) ? loaded.topicDomains : [];
    loaded.initiativeHistory = Array.isArray(loaded.initiativeHistory) ? loaded.initiativeHistory : [];
    loaded.locationHistory = Array.isArray(loaded.locationHistory)
      ? cleanStateList(loaded.locationHistory, 12)
      : cleanStateList([loaded.scene.location], 12);
    loaded.adultConfirmed = loaded.adultConfirmed === true;
    loaded.matureMode = loaded.matureMode === true && loaded.adultConfirmed;
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
