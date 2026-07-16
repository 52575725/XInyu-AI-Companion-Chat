const { chromium } = require("C:/Users/魏旭浩/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.61.1/node_modules/playwright");

const edgePath = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const url = process.argv[2] || "http://127.0.0.1:8080/";

(async () => {
  const browser = await chromium.launch({ executablePath: edgePath, headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  await page.addInitScript(() => {
    localStorage.setItem("heart-talk-selected-character", "xu-tang");
    localStorage.removeItem("heart-talk-ai-v2:xu-tang");
    let turn = 0;
    window.fetch = async (requestUrl) => {
      if (String(requestUrl).includes("/api/status")) {
        return new Response(JSON.stringify({ configured: true, model: "test-model", version: "test" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      turn += 1;
      const phase = turn <= 12 ? "对峙" : turn <= 28 ? "试探" : turn <= 45 ? "松动" : turn <= 65 ? "信任" : turn <= 85 ? "暧昧" : "确认";
      return new Response(JSON.stringify({
        reply: `第${turn}轮，许棠根据刚才的测试记录给出新的判断，并把下一张观察表推到你面前。`,
        narration: turn % 10 === 0 ? `第${turn}轮测试结束，街机屏幕切换到新的记录页面。` : "",
        suggestions: [`继续核对第${turn}轮数据`, `先解释第${turn}轮判断的理由`],
        memory_updates: [], stored_memories: [], topic: `测试节点${turn}`,
        conversation_move: `推进记录${turn}`, interaction_pattern: "信息交换",
        topic_domain: turn % 2 ? "误会冲突" : "共同计划", initiative: "女主主动",
        topic_source: turn % 3 ? "当前矛盾" : "未完成事件",
        affinity_update: {
          delta: turn % 10 === 0 ? -2 : 1,
          reason: turn % 10 === 0 ? "这轮回避了具体问题" : "这轮愿意继续核对事实",
          reaction: turn % 10 === 0 ? "失望" : "欣赏",
          trigger: turn % 10 === 0 ? "敷衍" : "行动力",
        },
        arc_update: {
          phase,
          central_conflict: "两人对界面测试结果的解释仍有差异",
          shared_goal: "完成三组玩家测试并形成共同结论",
          last_beat: `第${turn}轮产生了新的测试证据`,
          tension_delta: turn < 45 ? -1 : 0,
          trust_delta: 1,
          resolved: turn === 90,
        },
        scene_update: {}, life_update: {}, user_message_type: "dialogue", user_action_narration: "",
      }), { status: 200, headers: { "Content-Type": "application/json" } });
    };
  });

  try {
    await page.goto(url, { waitUntil: "networkidle" });
    for (let turn = 1; turn <= 100; turn += 1) {
      await page.locator("#messageInput").fill(`这是第${turn}轮，我继续谈当前测试矛盾。`);
      await page.locator("#chatForm").evaluate((form) => form.requestSubmit());
      await page.waitForFunction(() => !document.querySelector("#sendButton").disabled);
    }

    const result = await page.evaluate(() => {
      const state = JSON.parse(localStorage.getItem("heart-talk-ai-v2:xu-tang"));
      const composer = document.querySelector(".composer").getBoundingClientRect();
      return {
        turns: state.turns,
        messages: state.messages.length,
        topicHistory: state.topicHistory.length,
        moveHistory: state.moveHistory.length,
        suggestionHistory: state.suggestionHistory.length,
        replyOpenings: state.replyOpenings.length,
        uniqueReplyOpenings: new Set(state.replyOpenings).size,
        storyBeats: state.storyBeats.length,
        topicSources: state.topicSourceHistory.length,
        phase: state.arc.phase,
        trust: state.arc.trust,
        tension: state.arc.tension,
        affinity: state.affinity,
        progressWidth: document.querySelector("#progressBar").style.width,
        storyConflict: document.querySelector("#storyConflict").textContent,
        horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth,
        composerVisible: composer.top >= 0 && composer.bottom <= window.innerHeight,
      };
    });

    if (result.turns !== 100) throw new Error(`expected 100 turns, got ${result.turns}`);
    if (result.messages < 200 || result.messages > 220) throw new Error(`unexpected message count: ${result.messages}`);
    if (result.topicHistory !== 80 || result.moveHistory !== 60) throw new Error(`history caps failed: ${JSON.stringify(result)}`);
    if (result.suggestionHistory !== 100 || result.replyOpenings !== 100 || result.storyBeats !== 80 || result.topicSources !== 60) {
      throw new Error(`long history caps failed: ${JSON.stringify(result)}`);
    }
    if (result.uniqueReplyOpenings !== 100) throw new Error("reply opening history contains duplicates");
    if (result.phase !== "确认" || result.trust > 100 || result.tension < 0) throw new Error(`arc state invalid: ${JSON.stringify(result)}`);
    if (result.affinity !== 74 || result.progressWidth !== "74%") throw new Error(`affinity state invalid: ${JSON.stringify(result)}`);
    if (!result.storyConflict || result.horizontalOverflow || !result.composerVisible) throw new Error(`layout/state failed: ${JSON.stringify(result)}`);
    if (consoleErrors.length) throw new Error(`console errors: ${consoleErrors.join(" | ")}`);
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  } finally {
    await browser.close();
  }
})().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
