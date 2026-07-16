const { chromium } = require("C:/Users/魏旭浩/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.61.1/node_modules/playwright");

const edgePath = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const url = process.argv[2] || "http://127.0.0.1:8080/";

(async () => {
  const browser = await chromium.launch({ executablePath: edgePath, headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.addInitScript(() => {
    localStorage.setItem("heart-talk-selected-character", "shen-lan");
    localStorage.removeItem("heart-talk-ai-v2:shen-lan");
    let requests = 0;
    window.fetch = async (requestUrl) => {
      if (String(requestUrl).includes("/api/status")) {
        return new Response(JSON.stringify({ configured: true, model: "test-model" }), { status: 200 });
      }
      requests += 1;
      if (requests === 2) {
        return new Response(JSON.stringify({ error: "simulated failure" }), {
          status: 503,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response(JSON.stringify({
        reply: "拿安全当玩笑，不会让刚才的冒险显得更轻松。我需要确认你能认真对待这件事。",
        narration: "",
        suggestions: ["你说得对，我刚才是在回避风险", "我只是想缓和气氛，但我不认同你全盘否定我"],
        memory_updates: [], stored_memories: [], topic: "安全分寸",
        conversation_move: "明确边界", interaction_pattern: "直接回应",
        topic_domain: "误会冲突", initiative: "女主主动", topic_source: "当前矛盾",
        affinity_update: { delta: -3, reason: "用玩笑回避安全提醒", reaction: "警惕", trigger: "油嘴滑舌" },
        arc_update: { phase: "对峙", central_conflict: "", shared_goal: "", last_beat: "沈岚要求认真面对风险", tension_delta: 1, trust_delta: -1, resolved: false },
        scene_update: {}, life_update: {}, user_message_type: "dialogue", user_action_narration: "",
      }), { status: 200, headers: { "Content-Type": "application/json" } });
    };
  });

  try {
    await page.goto(url, { waitUntil: "networkidle" });
    await page.locator("#messageInput").fill("别这么严肃，我这不是好好的吗");
    await page.locator("#chatForm").evaluate((form) => form.requestSubmit());
    await page.waitForFunction(() => !document.querySelector("#sendButton").disabled);
    const afterSuccess = await page.evaluate(() => {
      const state = JSON.parse(localStorage.getItem("heart-talk-ai-v2:shen-lan"));
      return { affinity: state.affinity, turns: state.turns, progress: document.querySelector("#progressBar").style.width };
    });

    await page.locator("#messageInput").fill("再试一次");
    await page.locator("#chatForm").evaluate((form) => form.requestSubmit());
    await page.waitForFunction(() => !document.querySelector("#sendButton").disabled);
    const afterFailure = await page.evaluate(() => {
      const state = JSON.parse(localStorage.getItem("heart-talk-ai-v2:shen-lan"));
      return { affinity: state.affinity, turns: state.turns, progress: document.querySelector("#progressBar").style.width };
    });

    if (JSON.stringify(afterSuccess) !== JSON.stringify({ affinity: 1, turns: 1, progress: "3%" })) {
      throw new Error(`negative affinity was not applied: ${JSON.stringify(afterSuccess)}`);
    }
    if (JSON.stringify(afterFailure) !== JSON.stringify(afterSuccess)) {
      throw new Error(`failed request changed affinity or turns: ${JSON.stringify({ afterSuccess, afterFailure })}`);
    }
    process.stdout.write(`${JSON.stringify({ afterSuccess, afterFailure }, null, 2)}\n`);
  } finally {
    await browser.close();
  }
})().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
