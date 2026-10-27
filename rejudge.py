"""
CONSENSUS — re-judge an existing run.

Takes the drafts from a finished run (transcript.json) and has a different
judge score them again. The drafts stay exactly the same, so any change in
the result comes from the judge alone.

"""

import argparse
import asyncio
import copy
import json
import re
from pathlib import Path

import check_feasibility as cf
import run_consensus as rc


def strip_rulings(scenario: dict) -> dict:
    scenario = copy.deepcopy(scenario)
    for item in scenario["policy_dimensions"] + scenario["judge_flags"]:
        item.pop("scoring_note", None)
    return scenario


async def rejudge(transcript_path: Path, judge_model: str, rulings: bool) -> str:
    data = json.loads(transcript_path.read_text(encoding="utf-8"))
    variant = data["meta"]["scenario"] != "scenario_01"
    scenario = cf.load_scenario(variant)
    judge_scenario = scenario if rulings else strip_rulings(scenario)

    drafts = [rc.parse_draft(t["text"]) for t in data["transcript"] if "from_drafter" in t]
    old_scores = data["results"]["scores_by_draft"]

    new = []
    for i, d in enumerate(drafts):
        print(f"  Scoring Draft {i + 1} three times...")
        new.append(await rc.judge(judge_model, judge_scenario, d["draft"], i == 2))

    dims = rc.DIMENSIONS
    lines = [
        "CONSENSUS — re-judging",
        f"Transcript: {transcript_path}",
        f"Drafter: {data['meta']['drafter']}",
        f"Original judge: {data['meta']['judge']}",
        f"New judge: {judge_model}   Practitioner rulings shown: {'yes' if rulings else 'NO'}",
        "",
        "SCORES (original -> new; * marks a change)",
        "        " + "".join(f"{d[:8]:>10}" for d in dims),
    ]
    for i, (o, n) in enumerate(zip(old_scores, new)):
        cells = []
        for d in dims:
            mark = "*" if o[d] != n["scores"][d] else " "
            cells.append(f"{o[d]}->{n['scores'][d]}{mark}".rjust(10))
        lines.append(f"Draft {i + 1} " + "".join(cells))

    lines += ["", "NEW JUDGE'S QUOTED EVIDENCE FOR CHANGED SCORES"]
    for i, (o, n) in enumerate(zip(old_scores, new)):
        for d in dims:
            if o[d] != n["scores"][d]:
                quotes = {s["quotes"].get(d, "")[:140] for s in n["samples"]}
                lines.append(f"  Draft {i + 1} {d}: {o[d]} -> {n['scores'][d]}")
                lines += [f"      \"{q}\"" for q in quotes if q]

    lines += ["", "JUDGE CONSISTENCY (new judge, where its three scorings differed)"]
    lines += [f"  Draft {i + 1}: " + (", ".join(f"{d} {v}" for d, v in n["judge_disagreements"].items()) or "none")
              for i, n in enumerate(new)]

    # Final acceptance under the new judge's scores (always judged against
    # the scenario's actual rules).
    final = new[2]
    acc = cf.acceptance_check(scenario, final["scores"], final["flags"])
    accepted = sum(ok for ok, _ in acc.values())
    sg_ok = cf.secretary_general_ok(scenario, final["scores"])
    lines += ["", "FINAL TEXT UNDER THE NEW JUDGE",
              f"  Original result: {data['results']['accepted']}/7, consensus "
              f"{'TRUE' if data['results']['consensus'] else 'FALSE'}",
              f"  New result:      {accepted}/7, consensus "
              f"{'TRUE' if accepted == 7 and sg_ok else 'FALSE'}"]
    lines += [f"    {n:<10} {'ACCEPT' if ok else 'REJECT — ' + '; '.join(w)}"
              for n, (ok, w) in acc.items()]

    # What Round 2 would have looked like under the new judge's Draft 2 scores.
    _, library, variant_file = rc.load_all(variant)
    _, statuses, _, _ = rc.round_2_comments(scenario, library, variant_file,
                                            new[1]["scores"], new[1]["flags"])
    lines += ["", "ROUND 2 AS THE NEW JUDGE WOULD HAVE TRIGGERED IT",
              "  Original: " + ", ".join(f"{k} {v}" for k, v in data["results"]["round_2_statuses"].items()),
              "  New:      " + ", ".join(f"{k} {v}" for k, v in statuses.items()),
              "  (The drafts were written in response to the ORIGINAL Round 2. If these",
              "   differ, the negotiation itself would have gone differently.)"]
    report = "\n".join(lines)

    safe = re.sub(r"[^A-Za-z0-9.-]", "_", judge_model)
    tag = "rulings" if rulings else "no-rulings"
    out = transcript_path.parent / f"rejudge_{safe}_{tag}.txt"
    out.write_text(report, encoding="utf-8")
    full = transcript_path.parent / f"rejudge_{safe}_{tag}.json"
    full.write_text(json.dumps(new, indent=2, ensure_ascii=False), encoding="utf-8")
    return report + f"\n\nSaved to {out}"


def main():
    p = argparse.ArgumentParser(description="Re-score an existing run's drafts with another judge.")
    p.add_argument("transcript", help="path to a transcript.json")
    p.add_argument("--judge", required=True, help="judge model, e.g. openai/gpt-6.1-sol")
    p.add_argument("--no-rulings", action="store_true",
                   help="hide the practitioner rulings from the judge")
    args = p.parse_args()
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent / ".env")
    except ImportError:
        pass
    print(asyncio.run(rejudge(Path(args.transcript), args.judge, not args.no_rulings)))


if __name__ == "__main__":
    main()
