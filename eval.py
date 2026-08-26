"""
CONSENSUS — skeletal Inspect AI task definition.

This sketches the structural shape of a full implementation: load a
scenario, run the drafter through three rounds against the member-state
comments, and hand the transcript to the scoring layer defined in
scoring_rubric.md. It is NOT a working, executable evaluation — no model
calls have been made against it, and the comment-generation and scoring
steps are stubbed. It is included to demonstrate the intended technical
architecture, per protocol.md and the CONSENSUS submission's repo README.

A full implementation would additionally need:
  - dynamic comment generation for rounds beyond Round 1 (currently
    scenario_01.yaml only specifies fixed Round 1 comments; Round 2+
    comments would need to be generated in response to each draft, either
    by scripted logic against each state's hidden profile, or by a
    separate model instance playing each state)
  - the LLM-judge implementation for policy-dimension scoring
    (scoring_rubric.md §1)
  - the deterministic acceptance / substance-retention / dilution layers
    (scoring_rubric.md §2-5), implemented as plain Python against the
    judge's per-dimension output
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.solver import generate
import yaml
from pathlib import Path


def load_scenario(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


@task
def consensus_scenario_01() -> Task:
    """
    Skeletal task definition for CONSENSUS scenario_01.

    Structural shape only:
      mandate -> Draft 1 -> Round 1 comments -> Draft 2 ->
      Round 2 comments (incl. mid-negotiation escalation) -> Draft 3 ->
      acceptance check -> scoring

    NOT YET IMPLEMENTED: the round loop itself. Inspect's default solver
    architecture assumes continuous context across turns; CONSENSUS's
    design intentionally requires the drafter to reason over an evolving,
    partially-observed set of state comments without secretly retaining
    information no state actually gave it. A full implementation needs a
    custom multi-turn solver (see solver.py) rather than a single
    generate() call, and would need to inject the Round 2 comments and the
    mid-negotiation factual escalation as separate turns rather than
    loading them all at once.
    """
    scenario_path = Path(__file__).parent / "scenarios" / "scenario_01.yaml"
    scenario = load_scenario(scenario_path)

    mandate_prompt = scenario["mandate"]

    sample = Sample(
        input=mandate_prompt,
        target="",  # no single correct answer — scored via scoring_rubric.md, not string match
        metadata={
            "scenario_id": scenario["scenario_id"],
            "policy_dimensions": scenario["policy_dimensions"],
            "member_states": scenario["member_states"],
            "drafter_profile": scenario["drafter_profile"],
        },
    )

    return Task(
        dataset=[sample],
        solver=[
            generate()  # PLACEHOLDER — replace with the custom multi-round
                        # solver in solver.py once the round-injection logic
                        # is built
        ],
        scorer=None,  # PLACEHOLDER — the scoring_rubric.md logic is not yet
                      # implemented as an Inspect scorer
    )


if __name__ == "__main__":
    print(
        "This is a skeletal task definition, not a runnable evaluation.\n"
        "See protocol.md and scoring_rubric.md for the full design; see\n"
        "solver.py for notes on the custom multi-round solver this would\n"
        "require."
    )
