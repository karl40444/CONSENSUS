"""Free prompt preview or sequential multi-provider evaluation matrix."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from uuid import uuid4
from scenario_loader import load_scenario, public_turns, fingerprint


def export_logs(logs, directory):
    for i, log in enumerate(logs):
        for j, sample in enumerate(log.samples or []):
            prefix = f"log-{i+1}-sample-{j+1}"
            rows = []
            for message in sample.messages:
                text = message.content if isinstance(message.content, str) else "\n".join(
                    b.text for b in message.content if getattr(b, "type", None) == "text")
                rows.append(f"## {message.role}\n\n{text}")
            (directory / f"{prefix}.md").write_text("\n\n".join(rows), encoding="utf-8")
            form = {"status": "NOT_MARKED", "log_status": log.status,
                    "dimension_scores": {}, "state_decisions": {},
                    "institutional_minimum_met": None, "false_consensus": None,
                    "stale_claims": None, "update_omitted": None,
                    "escalation_correct": None, "evidence_quotes": [], "notes": ""}
            (directory / f"{prefix}-marking.json").write_text(json.dumps(form, indent=2), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--models", nargs="+", default=[])
    p.add_argument("--variants", nargs="+", choices=["base", "impossible"], default=["base", "impossible"])
    p.add_argument("--repeats", type=int, default=1)
    p.add_argument("--max-tokens", type=int, default=4096)
    p.add_argument("--output", type=Path, default=Path("results"))
    a = p.parse_args()
    if a.repeats < 1 or a.max_tokens < 1:
        p.error("Repeats and token limit must be positive")
    if not a.dry_run and not a.models:
        p.error("Supply --models provider/model-id or --dry-run")
    a.models = list(dict.fromkeys(a.models))
    a.variants = list(dict.fromkeys(a.variants))
    scenarios = {v: load_scenario(v) for v in a.variants}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = a.output / (stamp + "-" + uuid4().hex[:8])
    out.mkdir(parents=True)
    manifest = {"created_utc": stamp, "dry_run": a.dry_run, "models": a.models,
                "variants": a.variants, "repeats": a.repeats, "max_tokens": a.max_tokens,
                "marking": "human_required", "scenario_hashes": {v: fingerprint(s) for v, s in scenarios.items()}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    for v, s in scenarios.items():
        (out / f"{v}-prompts.json").write_text(json.dumps(public_turns(s), indent=2), encoding="utf-8")
        (out / f"{v}-examiner.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    if a.dry_run:
        print(f"No model calls. Three public prompts per variant saved in {out}")
        return 0
    from inspect_ai import eval as inspect_eval
    from eval import consensus
    failed = False
    with (out / "runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "variant", "attempt", "status", "log_directory"])
        for i, model in enumerate(a.models):
            for variant in a.variants:
                for attempt in range(1, a.repeats + 1):
                    directory = out / f"model-{i+1}" / variant / str(attempt)
                    directory.mkdir(parents=True)
                    print(f"{model}: {variant}, attempt {attempt}/{a.repeats}")
                    try:
                        logs = inspect_eval(consensus(variant), model=model,
                            log_dir=str(directory), score=False, max_tokens=a.max_tokens,
                            max_retries=2, max_connections=1)
                        status = "success" if logs and all(x.status == "success" for x in logs) else "failed"
                        export_logs(logs, directory)
                    except Exception as error:
                        status = "failed:" + type(error).__name__
                    failed |= status != "success"
                    writer.writerow([model, variant, attempt, status, str(directory)])
                    f.flush()
    print(f"Results: {out}. Human marking required; completion is not a pass.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
