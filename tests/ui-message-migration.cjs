const { chromium } = require("C:/Users/魏旭浩/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/.pnpm/playwright@1.61.1/node_modules/playwright");

const edgePath = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const url = process.argv[2] || "http://127.0.0.1:8080/";

(async () => {
  const browser = await chromium.launch({ executablePath: edgePath, headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 800 } });
  const page = await context.newPage();
  await page.addInitScript((saved) => {
    localStorage.setItem("heart-talk-ai-v1", JSON.stringify(saved));
  }, {
    turns: 3,
    messages: [
      { role: "user", text: "凑过去看屏幕，问她推荐哪里", time: 1 },
      { role: "assistant", text: "我指指屏幕上的直方图：‘其实调色前先看这个。’", time: 2 },
      { role: "narration", text: "林晚歪了歪头，嘴角带着一丝笑意。", time: 3 },
      { role: "assistant", text: "先说说看。", time: 4 },
      { role: "narration", text: "林晚歪了歪头，嘴角带着一丝笑意。", time: 5 },
      { role: "assistant", text: "（走到便利店门口，回头看你一眼）那我先进去。", time: 6 },
    ],
  });
  await page.goto(url, { waitUntil: "networkidle" });

  const result = await page.evaluate(() => ({
    userBubbles: [...document.querySelectorAll(".message-row.user .bubble")].map((node) => node.textContent),
    assistantBubbles: [...document.querySelectorAll(".message-row.assistant .bubble")].map((node) => node.textContent),
    narrations: [...document.querySelectorAll(".narration-row p")].map((node) => node.textContent),
  }));

  if (result.userBubbles.some((text) => text.includes("凑过去"))) throw new Error("stored user action still rendered as speech");
  if (result.assistantBubbles.some((text) => text.includes("我指指屏幕"))) throw new Error("stored assistant action still rendered as speech");
  if (result.assistantBubbles.some((text) => text.includes("走到便利店"))) throw new Error("parenthetical assistant action still rendered as speech");
  if (!result.assistantBubbles.includes("其实调色前先看这个。")) throw new Error("assistant spoken text was not preserved");
  if (!result.narrations.some((text) => text.includes("你凑过去看屏幕，问林晚推荐哪里。"))) throw new Error("user action narration missing");
  if (!result.narrations.some((text) => text.includes("林晚走到便利店门口，回头看你一眼。"))) throw new Error("parenthetical action narration missing");
  if (result.narrations.filter((text) => text === "林晚歪了歪头，嘴角带着一丝笑意。").length !== 1) {
    throw new Error("duplicate narration was not hidden");
  }

  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  await browser.close();
})().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exit(1);
});
