import json
import unittest
from unittest.mock import patch

import server


def valid_result(**overrides):
    result = {
        "reply": "我先认输，这个玩法再加码就没完了。说真的，我今天确实有点想出去走走。",
        "narration": "",
        "suggestions": ["那就不比了，聊聊你今天的事。", "你想去哪里走走？"],
        "memory_updates": [],
        "topic": "今日散步",
        "conversation_move": "收束玩笑",
        "interaction_pattern": "话题转场",
        "topic_domain": "共同计划",
        "initiative": "女主主动",
        "scene_update": {
            "location": "",
            "time": "",
            "activity": "",
            "add_props": [],
            "remove_props": ["冰淇淋"],
            "add_open_loops": ["周末去旧书店"],
            "close_open_loops": [],
        },
        "life_update": {
            "current_goal": "",
            "current_problem": "",
            "next_plan": "周末去旧书店找参考",
            "recent_event": "夜景构图终于定下了第一版",
        },
        "user_message_type": "dialogue",
        "user_action_narration": "",
    }
    result.update(overrides)
    return result


class ConversationStateTests(unittest.TestCase):
    def test_normalize_result_preserves_structured_updates(self):
        result = server.normalize_result(valid_result())

        self.assertEqual(result["interaction_pattern"], "话题转场")
        self.assertEqual(result["topic_domain"], "共同计划")
        self.assertEqual(result["initiative"], "女主主动")
        self.assertEqual(result["scene_update"]["remove_props"], ["冰淇淋"])
        self.assertEqual(result["life_update"]["next_plan"], "周末去旧书店找参考")

    def test_freeform_topic_domain_is_mapped_semantically(self):
        result = server.normalize_result(valid_result(
            topic="上楼看秘密",
            topic_domain="日常计划",
            reply="走吧，我们一起上楼看看。",
        ))

        self.assertEqual(result["topic_domain"], "共同计划")

    def test_leading_first_person_action_is_split_from_reply(self):
        result = server.normalize_result(valid_result(
            reply="我指指屏幕上的直方图：‘其实调色前先看这个，能少走很多弯路。’",
            narration="",
        ))

        self.assertEqual(result["reply"], "其实调色前先看这个，能少走很多弯路。")
        self.assertEqual(result["narration"], "林晚指指屏幕上的直方图。")

    def test_implicit_question_with_physical_action_becomes_narration(self):
        result = server.infer_user_action(
            {"latest_message": "凑过去看屏幕，问她推荐哪里"},
            server.normalize_result(valid_result(user_message_type="dialogue")),
        )

        self.assertEqual(result["user_message_type"], "action")
        self.assertEqual(result["user_action_narration"], "你凑过去看屏幕，问林晚推荐哪里。")

    def test_model_cannot_misclassify_plain_dialogue_as_action(self):
        result = server.infer_user_action(
            {"latest_message": "好啊，我倒要看看你能带我到哪里去。"},
            server.normalize_result(valid_result(
                user_message_type="action",
                user_action_narration="你挑了挑眉。",
            )),
        )

        self.assertEqual(result["user_message_type"], "dialogue")
        self.assertEqual(result["user_action_narration"], "")

    def test_parenthetical_assistant_action_is_split_and_suggestions_are_cleaned(self):
        result = server.normalize_result(valid_result(
            reply="（走到便利店门口，回头看你一眼）那我先进去，你在这里等我。",
            suggestions=["（站在原地，笑着摇头）好，我等你。", "我跟你一起进去。"],
        ))

        self.assertEqual(result["reply"], "那我先进去，你在这里等我。")
        self.assertEqual(result["narration"], "林晚走到便利店门口，回头看你一眼。")
        self.assertEqual(result["suggestions"][0], "好，我等你。")

    def test_user_action_pronouns_are_normalized(self):
        result = server.normalize_result(valid_result(
            user_message_type="action",
            user_action_narration="你后退半步，手抵住他的胸口。",
        ))

        self.assertEqual(result["user_action_narration"], "你后退半步，手抵住林晚的胸口。")

    def test_repeated_narration_requires_rewrite(self):
        narration = "林晚歪了歪头，嘴角带着一丝笑意。"
        result = server.normalize_result(valid_result(narration=narration))
        errors = server.hard_validation_errors(result, {
            "messages": [
                {"role": "narration", "text": narration},
                {"role": "assistant", "text": "先说说看。"},
                {"role": "user", "text": "好。"},
            ],
        })

        self.assertTrue(any("narration 重复" in error for error in errors))

    def test_suggestion_teacher_subject_inversion_requires_rewrite(self):
        result = server.normalize_result(valid_result(
            reply="我教你调色，你请我喝杯咖啡。",
            suggestions=["那你可得认真学，我要求很高。", "行，你认真教，我认真学。"],
        ))
        errors = server.hard_validation_errors(result, {})

        self.assertTrue(any("主语写反" in error for error in errors))

    def test_repeated_photography_material_forces_new_subject(self):
        data = {
            "latest_message": "那你说的秘密是什么？",
            "recent_topics": ["夜景构图", "照片调色"],
            "messages": [
                {"role": "assistant", "text": "我最近在研究摄影构图。"},
                {"role": "user", "text": "那你说的秘密是什么？"},
            ],
        }
        move = server.choose_director_move(data)
        errors = server.hard_validation_errors(
            server.normalize_result(valid_result(
                reply="我先教你怎么调色。",
                topic="照片调色",
                topic_domain="生活目标",
            )),
            data,
        )

        self.assertIn("素材疲劳强制转场", move)
        self.assertTrue(any("摄影绘画素材已经过度重复" in error for error in errors))
        self.assertTrue(any("男女关系张力" in error for error in errors))

    def test_surface_fatigue_cannot_pivot_only_to_food(self):
        data = {
            "latest_message": "凑过去看屏幕，问她推荐哪里",
            "recent_topics": ["夜景照片", "照片调色"],
            "messages": [
                {"role": "assistant", "text": "这张照片可以再调一下。"},
                {"role": "user", "text": "凑过去看屏幕，问她推荐哪里"},
            ],
        }
        result = server.normalize_result(valid_result(
            reply="附近新开了家串串店，要不要去试试？",
            topic="夜宵邀约",
            topic_domain="共同计划",
        ))
        errors = server.hard_validation_errors(result, data)

        self.assertTrue(any("普通日常活动" in error for error in errors))

    def test_relationship_pivot_may_use_one_old_detail_as_bridge(self):
        data = {
            "latest_message": "凑过去看屏幕，问她推荐哪里",
            "recent_topics": ["夜景照片", "照片调色"],
            "messages": [
                {"role": "assistant", "text": "这张照片可以再调一下。"},
                {"role": "user", "text": "凑过去看屏幕，问她推荐哪里"},
            ],
        }
        result = server.normalize_result(valid_result(
            reply="我有点好奇，你以前是不是也这样教过别人调色？",
            topic="试探前任",
            topic_domain="感情经历",
        ))
        errors = server.hard_validation_errors(result, data)

        self.assertFalse(any("素材已经过度重复" in error for error in errors))
        self.assertFalse(any("普通日常活动" in error for error in errors))

    def test_director_closes_two_rounds_of_playful_escalation(self):
        move = server.choose_director_move({
            "turns": 12,
            "latest_message": "那我就带十架无人机来找你",
            "recent_patterns": ["信息交换", "轻松对抗", "轻松对抗"],
        })

        self.assertIn("收束", move)

    def test_escalation_exchange_is_classified_as_playful_conflict(self):
        result = server.infer_interaction_pattern(
            {"latest_message": "那我带无人机追你"},
            server.normalize_result(valid_result(reply="那我就画一片乌云，看你怎么追。")),
        )

        self.assertEqual(result["interaction_pattern"], "轻松对抗")

    def test_third_playful_conflict_requires_targeted_rewrite(self):
        result = server.infer_interaction_pattern(
            {"latest_message": "那我带无人机追你"},
            server.normalize_result(valid_result(reply="那我就画一片乌云，看你怎么追。")),
        )
        errors = server.hard_validation_errors(
            result,
            {"recent_patterns": ["轻松对抗", "轻松对抗"]},
        )

        self.assertTrue(any("停止继续加码" in error for error in errors))

    def test_conditional_life_question_is_not_misclassified_as_escalation(self):
        result = server.infer_interaction_pattern(
            {"latest_message": "那我带无人机来找你"},
            server.normalize_result(valid_result(
                reply="你要是真对摄影有研究，可以给我的夜景构图提点建议。",
                interaction_pattern="生活分享",
            )),
        )

        self.assertEqual(result["interaction_pattern"], "生活分享")

    def test_build_messages_contains_scene_life_and_pattern_context(self):
        messages = server.build_messages({
            "turns": 8,
            "latest_message": "今天稿子画得怎么样？",
            "recent_patterns": ["生活分享"],
            "recent_topic_domains": ["生活目标"],
            "recent_initiatives": ["女主主动"],
            "scenario_id": "wrong-blind-date",
            "mature_mode": True,
            "adult_confirmed": True,
            "scene": {"location": "咖啡馆", "active_props": ["咖啡"]},
            "scene_age_turns": 2,
            "life": {"current_goal": "完成城市小册子"},
            "messages": [{"role": "user", "text": "今天稿子画得怎么样？"}],
        })
        context = json.loads(messages[1]["content"].split("：", 1)[1])

        self.assertEqual(context["当前场景状态"]["location"], "咖啡馆")
        self.assertEqual(context["当前生活线"]["current_goal"], "完成城市小册子")
        self.assertEqual(context["最近互动模式（同一种最多连续两轮）"], ["生活分享"])
        self.assertEqual(context["最近话题域（同一域不得连续三轮）"], ["生活目标"])
        self.assertEqual(context["最近主动性（连续两轮自然回应后必须女主主动）"], ["女主主动"])
        self.assertEqual(context["本轮禁用的疲劳素材（不得再提及或换同义词延续）"], [])
        self.assertEqual(context["开场场景编号"], "wrong-blind-date")
        self.assertTrue(context["成熟暧昧模式"])
        self.assertEqual(len(context["结合时间与上下文生成的场景候选（不是强制目的地）"]), 3)

    def test_mature_mode_requires_both_switch_and_adult_confirmation(self):
        messages = server.build_messages({
            "mature_mode": True,
            "adult_confirmed": False,
            "messages": [],
        })
        context = json.loads(messages[1]["content"].split("：", 1)[1])

        self.assertFalse(context["成熟暧昧模式"])
        self.assertFalse(context["已确认成年"])

    def test_two_passive_rounds_force_heroine_initiative(self):
        errors = server.hard_validation_errors(
            server.normalize_result(valid_result(initiative="自然回应")),
            {"recent_initiatives": ["自然回应", "自然回应"]},
        )

        self.assertTrue(any("女主已连续两轮被动" in error for error in errors))

    def test_three_rounds_in_same_topic_domain_force_switch(self):
        errors = server.hard_validation_errors(
            server.normalize_result(valid_result(topic_domain="吸引力")),
            {"recent_topic_domains": ["吸引力", "吸引力"]},
        )

        self.assertTrue(any("同一话题域已连续三轮" in error for error in errors))

    def test_third_question_ending_requires_rewrite(self):
        result = server.normalize_result(valid_result(reply="你会为了喜欢的人主动一次吗？"))
        errors = server.hard_validation_errors(result, {
            "messages": [
                {"role": "assistant", "text": "你第一次约会会选哪里？"},
                {"role": "user", "text": "随便走走。"},
                {"role": "assistant", "text": "那你会牵她的手吗？"},
                {"role": "user", "text": "看感觉。"},
            ],
        })

        self.assertTrue(any("连续三轮以问题结尾" in error for error in errors))

    def test_old_scene_forces_natural_scene_transition(self):
        errors = server.hard_validation_errors(
            server.normalize_result(valid_result(scene_update={})),
            {"scene_age_turns": 10},
        )

        self.assertTrue(any("场景停留过久" in error for error in errors))

    def test_director_prioritizes_initiative_and_scene_transition(self):
        initiative_move = server.choose_director_move({
            "turns": 12,
            "recent_initiatives": ["自然回应", "自然回应"],
        })
        scene_move = server.choose_director_move({
            "turns": 12,
            "scene_age_turns": 8,
            "recent_initiatives": ["女主主动"],
        })

        self.assertIn("强制女主主动", initiative_move)
        self.assertIn("两个反差选择", scene_move)

    def test_relationship_question_stays_in_current_scene(self):
        data = {
            "turns": 30,
            "latest_message": "你是不是很在意我和别的女生走得近？",
            "scene_age_turns": 12,
            "scene": {"location": "商场走廊", "time": "晚上九点"},
        }
        move = server.choose_director_move(data)
        result = server.normalize_result(valid_result(
            reply="我是在意，而且不想装作无所谓。",
            topic_domain="边界占有",
            scene_update={"location": "画馆"},
        ))
        errors = server.hard_validation_errors(result, data)

        self.assertIn("留在当前场景正面回应", move)
        self.assertTrue(any("换地点回避" in error for error in errors))

    def test_scene_candidates_fit_night_and_avoid_recent_location(self):
        candidates = server.scene_candidates({
            "turns": 18,
            "scenario_id": "access-card",
            "scene": {"location": "地铁口", "time": "晚上十一点"},
            "recent_locations": ["24小时书店"],
        })

        self.assertEqual(len(candidates), 3)
        self.assertTrue(all("24小时书店" not in candidate for candidate in candidates))
        self.assertTrue(any(place in " ".join(candidates) for place in ("江边", "夜市", "地铁", "Livehouse", "篮球场")))

    def test_default_art_location_is_rejected_when_user_did_not_choose_it(self):
        result = server.normalize_result(valid_result(
            scene_update={"location": "林晚的工作室"},
        ))
        errors = server.hard_validation_errors(result, {"latest_message": "那你想去哪？"})

        self.assertTrue(any("万能目的地" in error for error in errors))

    def test_broad_where_to_question_requires_choices_before_location_update(self):
        result = server.normalize_result(valid_result(
            reply="那就去江边吧。",
            scene_update={"location": "江边步道"},
        ))
        errors = server.hard_validation_errors(result, {
            "latest_message": "接下来去哪里比较合适？",
            "scene_age_turns": 9,
        })

        self.assertTrue(any("应给出两个合理选项" in error for error in errors))

    def test_two_scene_choices_satisfy_old_scene_transition_rule(self):
        result = server.normalize_result(valid_result(
            reply="我想到两个地方：去Livehouse街口走走，或者去篮球场看台坐会儿，你选哪种？",
            suggestions=["去Livehouse街口，热闹一点。", "去篮球场看台，安静一点。"],
            scene_update={},
        ))
        errors = server.hard_validation_errors(result, {
            "latest_message": "接下来去哪里？",
            "scene_age_turns": 12,
        })

        self.assertFalse(any("场景停留过久" in error for error in errors))

    def test_selected_scene_moves_forward_instead_of_repeating_choices(self):
        move = server.choose_director_move({
            "turns": 30,
            "latest_message": "篮球场看台听起来不错，安静一点好说话。",
            "scene_age_turns": 13,
            "scene": {"location": "商场走廊", "time": "晚上九点"},
        })

        self.assertIn("已经选定目的地", move)
        self.assertIn("更新 scene_update.location", move)

    def test_mature_director_introduces_closer_adult_topics(self):
        move = server.choose_director_move({
            "turns": 12,
            "mature_mode": True,
            "adult_confirmed": True,
            "recent_topic_domains": ["约会偏好"],
            "recent_initiatives": ["女主主动"],
        })

        self.assertIn("成熟暧昧推进", move)
        self.assertIn("亲吻", move)

    @patch("server.request_model")
    def test_format_repair_still_runs_quality_rewrite(self, request_model):
        repaired = valid_result(topic_domain="关系试探", initiative="自然回应")
        rewritten = valid_result(topic_domain="约会偏好", initiative="女主主动")
        request_model.side_effect = [
            {"choices": [{"message": {"content": "   "}}]},
            {"choices": [{"message": {"content": json.dumps(repaired, ensure_ascii=False)}}]},
            {"choices": [{"message": {"content": json.dumps(rewritten, ensure_ascii=False)}}]},
        ]

        with patch.object(server, "AI_API_KEY", "test-key"):
            result = server.call_model({
                "latest_message": "那你主动一点。",
                "recent_topic_domains": ["关系试探", "关系试探"],
                "recent_initiatives": ["自然回应", "自然回应"],
                "messages": [{"role": "user", "text": "那你主动一点。"}],
            })

        self.assertEqual(request_model.call_count, 3)
        self.assertEqual(result["topic_domain"], "约会偏好")
        self.assertEqual(result["initiative"], "女主主动")

    @patch("server.request_model")
    def test_domain_only_rewrite_failure_does_not_drop_reply(self, request_model):
        repeated = valid_result(
            reply="走吧，我们上楼再说。",
            topic="上楼看秘密",
            topic_domain="共同计划",
            initiative="女主主动",
        )
        request_model.side_effect = [
            {"choices": [{"message": {"content": json.dumps(repeated, ensure_ascii=False)}}]},
            {"choices": [{"message": {"content": json.dumps(repeated, ensure_ascii=False)}}]},
        ]

        with patch.object(server, "AI_API_KEY", "test-key"):
            result = server.call_model({
                "latest_message": "那就上去看看。",
                "recent_topic_domains": ["共同计划", "共同计划"],
                "messages": [{"role": "user", "text": "那就上去看看。"}],
            })

        self.assertEqual(result["reply"], "走吧，我们上楼再说。")
        self.assertNotEqual(result["topic_domain"], "共同计划")

    @patch("server.request_model")
    def test_repeated_suggestions_use_local_fallback_instead_of_error(self, request_model):
        repeated = valid_result(
            reply="我是在意，所以才想听你认真说。",
            suggestions=["什么条件？", "那你先说清楚。"],
            topic_domain="边界占有",
        )
        payload = {"choices": [{"message": {"content": json.dumps(repeated, ensure_ascii=False)}}]}
        request_model.side_effect = [payload, payload]

        with patch.object(server, "AI_API_KEY", "test-key"):
            result = server.call_model({
                "latest_message": "你是不是很在意？",
                "recent_suggestions": ["什么条件？", "那你先说清楚。"],
                "messages": [{"role": "user", "text": "你是不是很在意？"}],
            })

        self.assertEqual(result["reply"], repeated["reply"])
        self.assertNotEqual(result["suggestions"], repeated["suggestions"])

    def test_json_output_parses_without_repair_request(self):
        parsed = server.parse_model_output(json.dumps(valid_result(), ensure_ascii=False))

        self.assertEqual(parsed["reply"], valid_result()["reply"])
        self.assertEqual(parsed["interaction_pattern"], "话题转场")


if __name__ == "__main__":
    unittest.main()
