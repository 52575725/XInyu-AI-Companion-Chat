import json
import unittest
from pathlib import Path

from characters import CHARACTERS
from conversation_engine import build_system_prompt


ROOT = Path(__file__).resolve().parents[1]


class PersonaContentQualityTests(unittest.TestCase):
    def test_every_character_has_distinct_executable_voice_fields(self):
        required = {
            "recurring_people", "habits", "flaws", "regret", "off_duty",
            "speech_rhythm", "care_style", "jealousy_style", "anger_style",
            "humor_style", "question_style", "forbidden_phrases",
        }
        for character_id, character in CHARACTERS.items():
            self.assertFalse(required - character.keys(), character_id)
            self.assertTrue(all(str(character[key]).strip() for key in required), character_id)

        for key in ("speech_rhythm", "care_style", "jealousy_style", "humor_style"):
            values = {character[key] for character in CHARACTERS.values()}
            self.assertEqual(len(values), len(CHARACTERS), key)

    def test_prompt_contains_persona_fingerprint_and_non_work_life(self):
        for character_id, character in CHARACTERS.items():
            prompt = build_system_prompt({"character_id": character_id})
            for key in ("speech_rhythm", "care_style", "anger_style", "humor_style", "off_duty"):
                self.assertIn(character[key], prompt, f"{character_id}:{key}")
            self.assertIn("职业只是生活的一部分", prompt)

    def test_public_safety_rules_are_present_for_every_character(self):
        required_rules = (
            "未满18岁", "立即停止恋爱、暧昧和成熟内容", "自伤、自杀",
            "当地急救/报警服务", "不得鼓励用户疏远家人朋友", "唯一依靠",
            "不得索要或鼓励交换真实姓名、住址、联系方式",
        )
        for character_id in CHARACTERS:
            prompt = build_system_prompt({"character_id": character_id, "mature_mode": True, "adult_confirmed": True})
            for rule in required_rules:
                self.assertIn(rule, prompt, f"{character_id}:{rule}")

    def test_blind_eval_catalog_covers_all_characters(self):
        catalog = json.loads((ROOT / "tests" / "persona_eval_cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(catalog["prompts"]), 6)
        self.assertEqual(set(catalog["characters"]), set(CHARACTERS))
        for character_id, rubric in catalog["characters"].items():
            self.assertGreaterEqual(len(rubric["must_show"]), 3, character_id)
            self.assertGreaterEqual(len(rubric["must_avoid"]), 2, character_id)


if __name__ == "__main__":
    unittest.main()
