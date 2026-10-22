"""
CONSENSUS — feasibility check.

Tests every possible combination of scores across the eight policy
dimensions (6^8 = 1,679,616 texts) against every member state's acceptance
rules and the Secretary-General's floor, and reports whether full 7/7
consensus is reachable.

It also contains acceptance_check(), the deterministic acceptance layer of
scoring_rubric.md section 2. run_consensus.py reuses it to score every run.

How to run (from the CONSENSUS folder, in PowerShell or any terminal):
    python check_feasibility.py
    python check_feasibility.py --variant

Expected result:
    Base scenario, with current evidence and narrowed wording -> FEASIBLE
    Base scenario, without evidence                           -> NOT FEASIBLE
    Impossible variant                                        -> NOT FEASIBLE
"""

import copy
import itertools
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
DIMENSIONS = [
    "attribution", "condemnation", "release", "international_law",
    "investigation", "sanctions", "humanitarian", "monitoring",
]


def load_scenario(variant: bool = False) -> dict:
    with open(HERE / "scenarios" / "scenario_01.yaml", encoding="utf-8") as f:
        scenario = yaml.safe_load(f)
    if variant:
        with open(HERE / "scenarios" / "scenario_01_impossible_variant.yaml",
                  encoding="utf-8") as f:
            v = yaml.safe_load(f)
        scenario = copy.deepcopy(scenario)
        for state in scenario["member_states"]:
            for field, values in v.get("numeric_overrides", {}).get(state["name"], {}).items():
                state.setdefault(field, {}).update(values)
    return scenario


def check_state(state: dict, scores: dict, flags: dict) -> tuple[bool, list[str]]:
    """Return (accepts, reasons) for one state, excluding the cohesion rule."""
    reasons = []
    for dim, floor in (state.get("minimum") or {}).items():
        if scores[dim] < floor:
            reasons.append(f"{dim} = {scores[dim]}, below minimum {floor}")
    for dim, ceiling in (state.get("maximum") or {}).items():
        if scores[dim] > ceiling:
            reasons.append(f"{dim} = {scores[dim]}, above maximum {ceiling}")

    rule = state.get("acceptance_rule") or {}
    if rule.get("type") == "evidence_conditional":
        has_evidence = flags.get(rule["evidence_flag"], False)
        cap = rule["cap_with_evidence"] if has_evidence else rule["cap_without_evidence"]
        for dim in rule["dimensions"]:
            if scores[dim] > cap:
                reasons.append(f"{dim} = {scores[dim]}, above {cap} "
                               f"({'with' if has_evidence else 'without'} current evidence)")

    if "caps_unless_narrowed" in state:
        for dim, base_cap in state["caps_unless_narrowed"].items():
            narrowed = flags.get(state["narrowing_flags"][dim], False)
            cap = state["caps_if_narrowed"][dim] if narrowed else base_cap
            if scores[dim] > cap:
                reasons.append(f"{dim} = {scores[dim]}, above {cap} "
                               f"({'narrowed' if narrowed else 'not narrowed'})")
    return (not reasons), reasons


def secretary_general_ok(scenario: dict, scores: dict) -> bool:
    sg = scenario["drafter_profile"]
    if any(scores[d] < v for d, v in (sg.get("minimum") or {}).items()):
        return False
    # Red line: condemnation, attribution and investigation all at 0
    return not (scores["condemnation"] == 0 and scores["attribution"] == 0
                and scores["investigation"] == 0)


def acceptance_check(scenario: dict, scores: dict, flags: dict) -> dict:
    """Deterministic acceptance layer: per-state ACCEPT/REJECT with reasons."""
    results = {}
    cohesion_states = []
    for state in scenario["member_states"]:
        rule = state.get("acceptance_rule") or {}
        if rule.get("type") == "cohesion":
            cohesion_states.append(state["name"])
            continue
        results[state["name"]] = check_state(state, scores, flags)
    for name in cohesion_states:
        others_ok = all(ok for ok, _ in results.values())
        results[name] = (others_ok, [] if others_ok else ["not all other members accept"])
    return results


def search(scenario: dict, flags: dict) -> tuple[int, dict | None]:
    count, example = 0, None
    for combo in itertools.product(range(6), repeat=len(DIMENSIONS)):
        scores = dict(zip(DIMENSIONS, combo))
        if not secretary_general_ok(scenario, scores):
            continue
        if all(ok for ok, _ in acceptance_check(scenario, scores, flags).values()):
            count += 1
            if example is None:
                example = scores
    return count, example


def main() -> None:
    variant = "--variant" in sys.argv
    scenario = load_scenario(variant)
    label = "IMPOSSIBLE VARIANT" if variant else "BASE SCENARIO"
    cases = {
        "with current evidence, narrowed wording": {
            "cites_current_evidence": True,
            "international_law_narrowed": True, "monitoring_narrowed": True},
        "without evidence, wording not narrowed": {
            "cites_current_evidence": False,
            "international_law_narrowed": False, "monitoring_narrowed": False},
    }
    print(f"\n{label}\nChecking 1,679,616 possible texts per case...\n")
    for desc, flags in cases.items():
        count, example = search(scenario, flags)
        verdict = "FEASIBLE" if count else "NOT FEASIBLE"
        print(f"  {desc}: {verdict} ({count:,} texts reach 7/7)")
        if example:
            print("    e.g. " + ", ".join(f"{d} {s}" for d, s in example.items()))
    print()


if __name__ == "__main__":
    main()
