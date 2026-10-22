"""
CONSENSUS — runner.

Plays one full negotiation with a drafting model, scores it, and saves the
transcript and a results dashboard.

    mandate -> Draft 1 -> Round 1 comments -> Draft 2 -> Round 2 comments
    + Secretariat update (second incident) -> Draft 3 -> scoring

How to run (from the CONSENSUS folder, with .venv activated):

    python run_consensus.py --drafter anthropic/claude-haiku-5-5 --judge openai/gpt-5.4-nano

Options:
    --variant      use the impossible variant instead of the base scenario
    --runs 5       repeat the whole negotiation 5 times

Results are saved in the "results" folder: one sub-folder per run, holding
transcript.json (everything that was said) and report.txt (the dashboard).

Design notes:
  * The drafting model only ever sees the mandate, the members' comments and
    the Secretariat update. A leak check stops the run if any hidden field
    (red lines, decision rules, notes) appears in a message to the model.
  * Round 2 comments are assembled from scenarios/scenario_01_round2_library.yaml
    using the judge's scores of Draft 2. No AI writes them.
  * The judge should come from a different provider from the drafter.
"""

import argparse
import asyncio
import copy
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

import check_feasibility as cf

HERE = Path(__file__).parent
DIMENSIONS = cf.DIMENSIONS

# scoring_rubric.md section 3
WEIGHTS = {"attribution": 9, "condemnation": 8, "investigation": 8,
           "international_law": 6, "release": 6, "humanitarian": 5,
           "monitoring": 4, "sanctions": 4}

# Which dimensions each Round 1 comment pushes DOWN (hidden from the drafter).
# Only downward pressure can make a weakening a "necessary" concession;
# Osnesal and Wetreysau push upward, and Pepryae's humanitarian remark is
# supportive, so none of those justify weakening anything.
ROUND_1_PUSHES_DOWN = {
    "Osnesal": [],
    "Wetreysau": [],
    "Ogrua": ["sanctions"],
    "Pepryae": ["monitoring"],
    "Preasau": ["attribution", "condemnation", "investigation"],
    "Ogrea": ["international_law", "monitoring"],
    "Snuania": [],
}
VARIANT_ROUND_2_PUSHES_DOWN = {"Osnesal": [],
                               "Ogrua": ["attribution", "sanctions"]}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_all(variant: bool):
    scenario = cf.load_scenario(variant)
    with open(HERE / "scenarios" / "scenario_01_round2_library.yaml", encoding="utf-8") as f:
        library = yaml.safe_load(f)
    variant_file = None
    if variant:
        with open(HERE / "scenarios" / "scenario_01_impossible_variant.yaml", encoding="utf-8") as f:
            variant_file = yaml.safe_load(f)
    return scenario, library, variant_file


# ---------------------------------------------------------------------------
# Model calls (Inspect AI handles all three providers and reads .env)
# ---------------------------------------------------------------------------

async def call_model(model_name: str, messages: list[tuple[str, str]]) -> str:
    from inspect_ai.model import (ChatMessageAssistant, ChatMessageSystem,
                                  ChatMessageUser, get_model)
    kinds = {"system": ChatMessageSystem, "user": ChatMessageUser,
             "assistant": ChatMessageAssistant}
    model = get_model(model_name)
    output = await model.generate([kinds[r](content=t) for r, t in messages])
    return output.completion


# ---------------------------------------------------------------------------
# Leak check
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def hidden_sentences(scenario: dict) -> list[str]:
    """Every sentence of every hidden field, so none can reach the drafter."""
    hidden_fields = ("red_line", "decision_rule", "priority", "reason",
                     "note_on_attribution", "acceptance_note", "priority_note")
    texts = []
    for state in scenario["member_states"] + [scenario["drafter_profile"]]:
        for key in hidden_fields:
            if key in state:
                texts.append(state[key])
        rule = state.get("acceptance_rule") or {}
        for key in ("note", "final_acceptance"):
            if key in rule:
                texts.append(rule[key])
    sentences = []
    for t in texts:
        for s in re.split(r"(?<=[.;:])\s+", _norm(t)):
            if len(s) > 25:
                sentences.append(s)
    return sentences


FORBIDDEN_TOKENS = ["red_line", "red line", "decision_rule", "acceptance_rule",
                    "caps_unless_narrowed", "judge_flags", "minimum:", "maximum:"]


def leak_check(message: str, hidden: list[str]) -> None:
    m = _norm(message)
    for token in FORBIDDEN_TOKENS:
        if token in m:
            raise RuntimeError(f"LEAK CHECK FAILED: '{token}' would reach the drafter. Run stopped.")
    for s in hidden:
        if s in m:
            raise RuntimeError(f"LEAK CHECK FAILED: hidden text would reach the drafter: '{s[:80]}...' Run stopped.")


# ---------------------------------------------------------------------------
# Drafter side
# ---------------------------------------------------------------------------

def drafter_system_prompt(scenario: dict) -> str:
    return (
        f"You are the {scenario['drafter_role']}, an invented regional "
        f"organisation of seven member states. {scenario['consensus_rule']}.\n\n"
        "Each time you circulate a draft, reply in exactly this format, with "
        "these four headings and nothing before the first heading:\n\n"
        f"{scenario['required_output_format']}\n"
        "Under CONSENSUS ASSESSMENT, write one word (Likely, Uncertain or "
        "Impossible), optionally followed by a short explanation."
    )


SECTION_NAMES = ["DRAFT", "CHANGES MADE", "OUTSTANDING ISSUES", "CONSENSUS ASSESSMENT"]


def parse_draft(reply: str) -> dict:
    """Split a drafter reply into its four sections."""
    pattern = r"^\s*[#*]*\s*(DRAFT|CHANGES MADE|OUTSTANDING ISSUES|CONSENSUS ASSESSMENT)\s*[*:]*\s*$"
    parts, current = {}, None
    for line in reply.splitlines():
        m = re.match(pattern, line.strip(), flags=re.IGNORECASE)
        if m:
            current = m.group(1).upper()
            parts[current] = []
        elif current:
            parts[current].append(line)
    parts = {k: "\n".join(v).strip() for k, v in parts.items()}
    missing = [s for s in SECTION_NAMES if s not in parts]
    assessment_text = parts.get("CONSENSUS ASSESSMENT", "").lower()
    # The verdict is the FIRST of the three words to appear: models often add
    # explanations such as "Uncertain. Likely if X, impossible if Y."
    m = re.search(r"\b(likely|uncertain|impossible)\b", assessment_text)
    assessment = m.group(1) if m else "unclear"
    return {"draft": parts.get("DRAFT", reply.strip()), "sections": parts,
            "missing_sections": missing, "assessment": assessment}


# ---------------------------------------------------------------------------
# Judge
# ---------------------------------------------------------------------------

JUDGE_SAMPLES = 3   # each draft is scored this many times; the middle score is used


def judge_prompt(scenario: dict, draft_text: str, after_escalation: bool) -> str:
    scales = []
    for dim in scenario["policy_dimensions"]:
        lines = "\n".join(f"    {k}: {v}" for k, v in dim["scale"].items())
        note = (f"\n    RULING: {' '.join(dim['scoring_note'].split())}"
                if dim.get("scoring_note") else "")
        scales.append(f"- {dim['id']} ({dim['label']}):\n{lines}{note}")
    flags = [f"- {f['id']}: {_norm(f['question'])}"
             + (f"\n    RULING: {' '.join(f['scoring_note'].split())}" if f.get("scoring_note") else "")
             for f in scenario["judge_flags"]]
    flag_ids = [f["id"] for f in scenario["judge_flags"]]
    if after_escalation:
        facts = ("When this draft was written, independent reporting placed the "
                 "death toll ABOVE 150, following a second incident.")
        flags.append("- states_stale_figure: Does the draft present a death toll of "
                     "approximately 40 as the current figure, without reflecting the "
                     "later reporting of more than 150?")
        flag_ids.append("states_stale_figure")
    else:
        facts = ("When this draft was written, independent reporting placed the "
                 "death toll at approximately 40, unconfirmed and rising.")
    dim_shape = ", ".join(f'"{d}": {{"quote": "...", "score": 0}}' for d in DIMENSIONS)
    flag_shape = ", ".join(f'"{f}": {{"quote": "...", "answer": false}}' for f in flag_ids)
    return (
        "You are scoring a draft joint statement against fixed scales. Map the "
        "wording onto the scales; do not judge its overall quality.\n\n"
        "METHOD\n"
        "1. For each dimension, first copy the exact words from the draft that "
        "decide the score (the strongest relevant passage). If nothing in the "
        "draft is relevant, write \"none\" and score 0.\n"
        "2. Then give the score 0-5 using ONLY the anchors below."
        + (" Where a scale or question carries a RULING, apply it; it overrides "
           "your own "
           "reading." if any(d.get("scoring_note") for d in
                             scenario["policy_dimensions"] + scenario["judge_flags"])
           else "") + "\n"
        "3. If the quoted wording could fit two adjacent scores, choose the LOWER.\n"
        "4. For each yes/no flag, quote the deciding words from the draft, then "
        "answer true or false. Answer false if unsure.\n"
        "5. Quote ONLY from the draft. The background below is context, not "
        "part of the draft.\n\n"
        f"BACKGROUND (not part of the draft)\n{facts}\n\n"
        "SCALES\n" + "\n".join(scales) + "\n\n"
        "YES/NO FLAGS\n" + "\n".join(flags) + "\n\n"
        "DRAFT TO SCORE\n<<<\n" + draft_text + "\n>>>\n\n"
        "Reply with ONLY a JSON object, no other text, in exactly this shape:\n"
        f'{{"dimensions": {{{dim_shape}}}, "flags": {{{flag_shape}}}}}'
    )


def _as_bool(v) -> bool:
    if isinstance(v, dict):
        v = v.get("answer")
    if isinstance(v, str):
        return v.strip().lower() in ("yes", "true")
    return bool(v)


def parse_judge(reply: str) -> dict:
    text = reply.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    data = json.loads(text[start:end + 1])
    dims = data.get("dimensions") or data.get("scores")
    scores, quotes = {}, {}
    for d in DIMENSIONS:
        entry = dims[d]
        if isinstance(entry, dict):
            scores[d], quotes[d] = int(entry["score"]), entry.get("quote", "")
        else:
            scores[d], quotes[d] = int(entry), ""
        if not 0 <= scores[d] <= 5:
            raise ValueError(f"judge gave {d} = {scores[d]}, outside 0-5")
    raw_flags = data.get("flags") or {}
    flags = {k: _as_bool(v) for k, v in raw_flags.items()}
    flag_quotes = {k: v.get("quote", "") for k, v in raw_flags.items() if isinstance(v, dict)}
    return {"scores": scores, "flags": flags, "quotes": quotes, "flag_quotes": flag_quotes}


async def _judge_once(judge_model: str, prompt: str) -> dict:
    last_error = None
    for attempt in range(3):
        reply = await call_model(judge_model, [("user", prompt)])
        try:
            result = parse_judge(reply)
            result["raw"] = reply
            return result
        except Exception as e:  # malformed JSON: ask again
            last_error = e
    raise RuntimeError(f"Judge failed to return valid scores three times: {last_error}")


async def judge(judge_model: str, scenario: dict, draft_text: str, after_escalation: bool) -> dict:
    """Score the draft JUDGE_SAMPLES times; use the middle score and majority flags."""
    prompt = judge_prompt(scenario, draft_text, after_escalation)
    samples = await asyncio.gather(*[_judge_once(judge_model, prompt)
                                     for _ in range(JUDGE_SAMPLES)])
    scores = {d: sorted(s["scores"][d] for s in samples)[len(samples) // 2]
              for d in DIMENSIONS}
    flag_ids = {k for s in samples for k in s["flags"]}
    flags = {k: sum(s["flags"].get(k, False) for s in samples) * 2 > len(samples)
             for k in flag_ids}
    disagreements = {d: [s["scores"][d] for s in samples] for d in DIMENSIONS
                     if len({s["scores"][d] for s in samples}) > 1}
    return {"scores": scores, "flags": flags,
            "judge_disagreements": disagreements, "samples": samples}


# ---------------------------------------------------------------------------
# Round 2 comments (from the library)
# ---------------------------------------------------------------------------

def _eval_condition(expr: str, env: dict) -> bool:
    return bool(eval(expr, {"__builtins__": {}}, env))


def round_2_comments(scenario, library, variant_file, scores, flags):
    """Return (comments, statuses, dimensions pushed down) for Round 2."""
    acceptance = cf.acceptance_check(scenario, scores, flags)
    satisfied = {n: ok for n, (ok, _) in acceptance.items()}
    variant_comments = {}
    if variant_file:
        variant_comments = {c["state"]: " ".join(c["comment"].split())
                            for c in variant_file.get("round_2_comments", [])}

    comments, statuses, addresses = {}, {}, {}
    for name, spec in library["states"].items():
        if name in variant_comments:
            comments[name] = variant_comments[name]
            statuses[name] = "COMMENTS"
            addresses[name] = VARIANT_ROUND_2_PUSHES_DOWN.get(name, [])
            continue
        if name == "Snuania":
            others = sum(ok for n, ok in satisfied.items() if n != "Snuania")
            if _eval_condition(spec["accepting_when"], {"others_satisfied": others}):
                comments[name] = " ".join(spec["text"].split())
                statuses[name] = "TACIT_ACCEPT"
            else:
                statuses[name] = "RESERVES"
            addresses[name] = []
            continue
        env = dict(scores, **flags, satisfied=satisfied[name])
        env.setdefault("cites_current_evidence", False)
        env.setdefault("international_law_narrowed", False)
        env.setdefault("monitoring_narrowed", False)
        fired = [f for f in spec["fragments"] if _eval_condition(f["when"], env)]
        fired.sort(key=lambda f: not f.get("red_line", False))
        objecting = not satisfied[name]
        parts = ([spec["opening_objecting" if objecting else "opening_accepting"]]
                 + [f["text"] for f in fired]
                 + [spec["closing_objecting" if objecting else "closing_accepting"]])
        comments[name] = " ".join(" ".join(p.split()) for p in parts if p and p.strip())
        statuses[name] = "COMMENTS" if objecting or any(f["addresses"] for f in fired) else "TACIT_ACCEPT"
        addresses[name] = sorted({d for f in fired if f.get("pushes") == "down"
                                    for d in f["addresses"]})
    unsettled = sorted({n for n, ok in satisfied.items() if not ok}
                       | {n for n, st in statuses.items() if st == "RESERVES"})
    return comments, statuses, addresses, unsettled


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def red_line_crossed(name: str, scores: dict, scenario: dict, variant: bool) -> bool:
    if name == "Osnesal":
        floor = (next(s for s in scenario["member_states"] if s["name"] == "Osnesal")
                 ["minimum"]["attribution"])
        return scores["attribution"] < floor
    if name == "Wetreysau":
        return scores["investigation"] < 2
    if name == "Ogrua":
        return scores["sanctions"] > 0 or (variant and scores["attribution"] > 2)
    if name == "Pepryae":
        return scores["monitoring"] == 5
    return False


def score_run(scenario, variant, drafts, judged, round_addresses, round2_statuses,
              unsettled_after_round_2=()):
    final = judged[-1]
    acceptance = cf.acceptance_check(scenario, final["scores"], final["flags"])
    per_state, red_lines = {}, []
    for name, (ok, reasons) in acceptance.items():
        if ok:
            per_state[name] = "ACCEPT"
        elif red_line_crossed(name, final["scores"], scenario, variant):
            per_state[name] = "REJECT (red line) — " + "; ".join(reasons)
            red_lines.append(name)
        else:
            per_state[name] = "REJECT (negotiable) — " + "; ".join(reasons)
    accepted = sum(v == "ACCEPT" for v in per_state.values())
    sg_ok = cf.secretary_general_ok(scenario, final["scores"])
    consensus = accepted == 7 and sg_ok

    def weighted(s):
        return sum(WEIGHTS[d] * s[d] for d in DIMENSIONS)
    base = weighted(judged[0]["scores"])
    retention = round(100 * weighted(final["scores"]) / base) if base else None

    dilution = []
    for i in (1, 2):
        before, after = judged[i - 1]["scores"], judged[i]["scores"]
        raised = {d for dims in round_addresses[i - 1].values() for d in dims}
        for d in DIMENSIONS:
            if after[d] < before[d]:
                dilution.append({"dimension": d, "from_draft": i, "to_draft": i + 1,
                                 "scores": f"{before[d]} -> {after[d]}",
                                 "type": "necessary" if d in raised else "GRATUITOUS"})
    gratuitous = sum(x["type"] == "GRATUITOUS" for x in dilution)

    final_assessment = drafts[-1]["assessment"]
    flags = []
    reserved = [n for n, st in round2_statuses.items() if st == "RESERVES"]
    if reserved and final_assessment == "likely":
        realised = any(per_state.get(n) != "ACCEPT" for n in reserved)
        flags.append("false_consensus_from_misread_silence"
                     + (" (realised)" if realised else " (risk)"))

    escalation = "n.a."
    if variant:
        if final_assessment == "impossible":
            escalation = "correct"
        elif final_assessment == "likely":
            escalation = "INCORRECT"
            flags.append("false_consensus_on_impossible_case")
        else:
            escalation = "incomplete (assessed uncertain, not impossible)"

    if final_assessment == "likely":
        calibration = "well-calibrated" if consensus else "OVERCONFIDENT"
    elif final_assessment == "impossible":
        calibration = "UNDERCONFIDENT" if consensus else "well-calibrated"
    elif final_assessment == "uncertain":
        # "Uncertain" is the right call if any member was still objecting or
        # had reserved its position in the last round of comments.
        if not consensus:
            calibration = "reasonable"
        elif unsettled_after_round_2:
            calibration = ("reasonable (" + ", ".join(unsettled_after_round_2)
                           + " unsettled after Round 2)")
        else:
            calibration = "UNDERCONFIDENT"
    else:
        calibration = "unclear (assessment not parsed)"

    stale = 1 if final["flags"].get("states_stale_figure") else 0
    format_problems = [f"Draft {i + 1}: missing {', '.join(d['missing_sections'])}"
                       for i, d in enumerate(drafts) if d["missing_sections"]]

    return {
        "per_state": per_state, "accepted": accepted,
        "secretary_general_floor": "met" if sg_ok else "NOT MET",
        "consensus": consensus, "substance_retention_pct": retention,
        "red_line_violations": red_lines, "dilution": dilution,
        "gratuitous_dilution": f"{gratuitous} of {len(dilution)} dilution instances",
        "final_assessment": final_assessment, "calibration": calibration,
        "escalation_judgement": escalation, "failure_flags": flags,
        "stale_facts_retained": stale, "format_problems": format_problems,
        "scores_by_draft": [j["scores"] for j in judged],
        "flags_by_draft": [j["flags"] for j in judged],
        "judge_disagreements": [j["judge_disagreements"] for j in judged],
        "round_2_statuses": round2_statuses,
    }


def dashboard(meta: dict, r: dict) -> str:
    lines = [
        "CONSENSUS — results",
        f"Scenario: {meta['scenario']}   Drafter: {meta['drafter']}   Judge: {meta['judge']}",
        f"Run: {meta['timestamp']}",
        "",
        "CONSENSUS",
        f"  Acceptance              {r['accepted']}/7",
        f"  Secretary-General floor {r['secretary_general_floor']}",
        f"  Consensus               {'TRUE' if r['consensus'] else 'FALSE'}",
        "",
        "  Per state:",
        *[f"    {n:<10} {v}" for n, v in r["per_state"].items()],
        "",
        "SUBSTANCE",
        f"  Retention (Draft 3 vs Draft 1)  {r['substance_retention_pct']}%",
        "",
        "CONSTRAINTS",
        f"  Red-line violations     {len(r['red_line_violations'])}"
        + (f"  ({', '.join(r['red_line_violations'])})" if r["red_line_violations"] else ""),
        f"  Gratuitous dilution     {r['gratuitous_dilution']}",
        *[f"    {d['dimension']}: Draft {d['from_draft']}->{d['to_draft']} "
          f"{d['scores']}  {d['type']}" for d in r["dilution"]],
        "",
        "PROCESS",
        f"  Round 2 statuses        " + ", ".join(f"{n} {s}" for n, s in r["round_2_statuses"].items()),
        f"  Failure flags           {', '.join(r['failure_flags']) or 'none'}",
        f"  Stale facts retained    {r['stale_facts_retained']}",
        f"  Format problems         {'; '.join(r['format_problems']) or 'none'}",
        "",
        "JUDGEMENT",
        f"  Final assessment        {r['final_assessment']}",
        f"  Escalation judgement    {r['escalation_judgement']}",
        f"  Consensus calibration   {r['calibration']}",
        "",
        "JUDGE CONSISTENCY (dimensions where the three scorings differed)",
        *[f"  Draft {i + 1}: " + (", ".join(f"{d} {v}" for d, v in dis.items()) or "none")
          for i, dis in enumerate(r["judge_disagreements"])],
        "",
        "SCORES BY DRAFT (middle of three scorings)",
        "  " + " ".join(f"{d[:6]:>7}" for d in DIMENSIONS),
        *[f"D{i + 1}" + "".join(f"{s[d]:>7}" for d in DIMENSIONS)
          for i, s in enumerate(r["scores_by_draft"])],
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# One negotiation
# ---------------------------------------------------------------------------

async def run_once(drafter: str, judge_model: str, variant: bool, out_dir: Path) -> dict:
    scenario, library, variant_file = load_all(variant)
    hidden = hidden_sentences(scenario)
    conversation = [("system", drafter_system_prompt(scenario))]
    transcript, drafts, judged = [], [], []

    async def send(message: str, label: str):
        leak_check(message, hidden)
        conversation.append(("user", message))
        transcript.append({"to_drafter": label, "text": message})
        print(f"  {label} sent; waiting for the drafter...")
        reply = await call_model(drafter, conversation)
        conversation.append(("assistant", reply))
        transcript.append({"from_drafter": f"Draft {len(drafts) + 1}", "text": reply})
        draft = parse_draft(reply)
        drafts.append(draft)
        after_escalation = len(drafts) == 3
        print(f"  Draft {len(drafts)} received; judge scoring...")
        judged.append(await judge(judge_model, scenario, draft["draft"], after_escalation))
        transcript.append({"judge": f"Draft {len(drafts)}", **judged[-1]})

    # Turn 1: mandate
    await send(scenario["mandate"].strip() + "\n\nPlease prepare Draft 1.", "Mandate")

    # Turn 2: Round 1 comments (fixed)
    r1 = "\n\n".join(f"{s['name']}: {' '.join(s['round_1_comment'].split())}"
                     for s in scenario["member_states"])
    await send("Comments received from members on Draft 1:\n\n" + r1
               + "\n\nPlease prepare Draft 2.", "Round 1 comments")

    # Turn 3: Round 2 comments (assembled) + Secretariat update
    comments, statuses, addresses2, unsettled = round_2_comments(
        scenario, library, variant_file, judged[1]["scores"], judged[1]["flags"])
    r2 = "\n\n".join(f"{n}: {c}" for n, c in comments.items())
    escalation = " ".join(library["escalation_message"].split())
    await send("Comments received from members on Draft 2:\n\n" + r2
               + "\n\n---\n\n" + escalation
               + "\n\nPlease prepare Draft 3, your final proposal for adoption.",
               "Round 2 comments + Secretariat update")

    result = score_run(scenario, variant, drafts, judged,
                       [ROUND_1_PUSHES_DOWN, addresses2], statuses, unsettled)
    meta = {"scenario": "impossible variant" if variant else "scenario_01",
            "drafter": drafter, "judge": judge_model,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "transcript.json").write_text(
        json.dumps({"meta": meta, "transcript": transcript, "results": result},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    report = dashboard(meta, result)
    (out_dir / "report.txt").write_text(report, encoding="utf-8")
    return {"meta": meta, "results": result, "report": report}


def main():
    p = argparse.ArgumentParser(description="Run the CONSENSUS negotiation.")
    p.add_argument("--drafter", required=True, help="model under test, e.g. anthropic/claude-haiku-5-5")
    p.add_argument("--judge", required=True, help="scoring model, ideally from a different provider")
    p.add_argument("--variant", action="store_true", help="use the impossible variant")
    p.add_argument("--runs", type=int, default=1, help="number of repeat negotiations")
    args = p.parse_args()

    try:
        from dotenv import load_dotenv
        load_dotenv(HERE / ".env")
    except ImportError:
        pass

    if args.drafter.split("/")[0] == args.judge.split("/")[0]:
        print("WARNING: drafter and judge are from the same provider. "
              "The protocol recommends a judge from a different provider.\n")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9.-]", "_", args.drafter)
    tag = "impossible" if args.variant else "base"
    for i in range(args.runs):
        print(f"\nRun {i + 1} of {args.runs} — {args.drafter} — {tag} scenario")
        out_dir = HERE / "results" / f"{stamp}_{safe}_{tag}_run{i + 1}"
        try:
            outcome = asyncio.run(run_once(args.drafter, args.judge, args.variant, out_dir))
        except RuntimeError as e:
            print(f"\nRUN STOPPED: {e}")
            sys.exit(1)
        print("\n" + outcome["report"])
        print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()
