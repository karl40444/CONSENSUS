"""Runnable task; substantive scoring remains human-reviewed."""
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from scenario_loader import load_scenario, public_turns, fingerprint
from solver import consensus_solver


@task
def consensus(variant: str = "base") -> Task:
    data = load_scenario(variant)
    turns = public_turns(data)
    return Task(dataset=[Sample(id=variant, input=turns[0], metadata={
        "variant": variant, "scenario_sha256": fingerprint(data),
        "marking": "human_required", "protocol": "fixed-comments-v0.2",
    })], solver=consensus_solver(turns), scorer=None)
