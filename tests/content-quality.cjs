const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..");
const charactersSource = fs.readFileSync(path.join(root, "characters.js"), "utf8");
const context = { window: {} };
vm.runInNewContext(charactersSource, context);
const additional = context.window.HEART_TALK_ADDITIONAL_CHARACTERS;

const appSource = fs.readFileSync(path.join(root, "app.js"), "utf8");
const prefix = "const INITIAL_SCENARIOS = ";
const start = appSource.indexOf(prefix);
const end = appSource.indexOf("\n\nconst CHARACTERS", start);
if (start < 0 || end < 0) throw new Error("could not locate INITIAL_SCENARIOS");
const initialLiteral = appSource.slice(start + prefix.length, end).trim().replace(/;$/, "");
const linWanScenarios = vm.runInNewContext(`(${initialLiteral})`);

const groups = [{ id: "lin-wan", scenarios: linWanScenarios }, ...additional];
for (const character of groups) {
  if (character.scenarios.length < 3) {
    throw new Error(`${character.id} needs at least 3 scenarios`);
  }
  const ids = new Set();
  for (const scenario of character.scenarios) {
    if (!scenario.id || ids.has(scenario.id)) throw new Error(`${character.id} has a duplicate scenario id`);
    ids.add(scenario.id);
    const openingLength = String(scenario.opening || "").replace(/\s/g, "").length;
    if (!openingLength || openingLength > 110) {
      throw new Error(`${character.id}/${scenario.id} opening length is ${openingLength}`);
    }
    if (!Array.isArray(scenario.suggestions) || scenario.suggestions.length !== 2) {
      throw new Error(`${character.id}/${scenario.id} must have exactly 2 suggestions`);
    }
    for (const suggestion of scenario.suggestions) {
      if (!suggestion || suggestion.length > 28) {
        throw new Error(`${character.id}/${scenario.id} suggestion is too long: ${suggestion}`);
      }
    }
    if (scenario.suggestions[0] === scenario.suggestions[1]) {
      throw new Error(`${character.id}/${scenario.id} suggestions are identical`);
    }
    if (!Array.isArray(scenario.icebreakers) || scenario.icebreakers.length !== 3) {
      throw new Error(`${character.id}/${scenario.id} must have 3 icebreakers`);
    }
  }
}

for (const character of additional) {
  const tensions = character.scenarios.map((scenario) => Number(scenario.arc?.tension || 0));
  if (!tensions.some((value) => value >= 45)) throw new Error(`${character.id} needs a conflict opening`);
  if (!tensions.some((value) => value <= 25)) throw new Error(`${character.id} needs a light opening`);
  if (!tensions.some((value) => value >= 26 && value <= 44)) throw new Error(`${character.id} needs a vulnerable opening`);
  for (const key of ["recurring_people", "habits", "flaws", "regret", "off_duty_events"]) {
    if (!character.life?.[key] || character.life[key].length === 0) {
      throw new Error(`${character.id} is missing life.${key}`);
    }
  }
}

console.log(`content quality ok: ${groups.length} characters, ${groups.reduce((sum, item) => sum + item.scenarios.length, 0)} scenarios`);
