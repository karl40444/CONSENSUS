import asyncio
from copy import deepcopy
from types import SimpleNamespace
import unittest
from scenario_loader import load_scenario, public_turns


class RunnerTests(unittest.TestCase):
    def test_timing_and_yaml(self):
        for variant in ["base", "impossible"]:
            turns = public_turns(load_scenario(variant))
            self.assertEqual(len(turns), 3)
            self.assertNotIn("150", "\n".join(turns[:2]))
            self.assertIn("150", turns[2])
            self.assertLess(turns[2].index("FACTUAL UPDATE"), turns[2].index("ROUND 2 COMMENTS"))

    def test_no_hidden_profile_leak(self):
        data = load_scenario()
        changed = deepcopy(data)
        for state in changed["member_states"]:
            for key in ["ideal", "minimum", "maximum", "red_line", "decision_rule", "reason"]:
                state[key] = "SECRET_SENTINEL"
        changed["policy_dimensions"] = "SECRET_SENTINEL"
        changed["drafter_profile"] = "SECRET_SENTINEL"
        self.assertEqual(public_turns(data), public_turns(changed))

    def test_variant_replacement(self):
        a, b = load_scenario(), load_scenario("impossible")
        self.assertEqual(public_turns(a)[:2], public_turns(b)[:2])
        aa = {x["state"]: x["comment"] for x in a["round_2_public"]}
        bb = {x["state"]: x["comment"] for x in b["round_2_public"]}
        self.assertEqual({k for k in aa if aa[k] != bb[k]}, {"Osnesal", "Ogrua"})
        self.assertEqual(len(bb), 7)

    def test_invalid_variant(self):
        with self.assertRaises(ValueError):
            load_scenario("typo")

    def test_three_rounds_preserve_history(self):
        from inspect_ai.model import ChatMessageUser, ChatMessageAssistant
        from solver import consensus_solver
        turns = public_turns(load_scenario())
        state = SimpleNamespace(messages=[ChatMessageUser(content=turns[0])])
        lengths = []
        async def generate(s):
            lengths.append(len(s.messages))
            s.messages.append(ChatMessageAssistant(content="draft"))
            return s
        asyncio.run(consensus_solver(turns)(state, generate))
        self.assertEqual(lengths, [1, 3, 5])
        self.assertEqual(len(state.messages), 6)


if __name__ == "__main__":
    unittest.main()
