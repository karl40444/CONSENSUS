# CONSENSUS

**Consensus-oriented Statement Evaluation for Negotiation, Synthesis and Unanimous Settlement**

An evaluation protocol for frontier AI models drafting consensus text on behalf of multilateral institutions — tested here through an invented scenario in which a model plays the Secretary-General of a fictional regional body, drafting a joint statement that seven member states, each with a private position voiced only in diplomatic language, must all accept.

## Why this exists

Governments are already using frontier models in foreign-policy workflows faster than anyone is measuring whether the models are any good at it. A July 2026 Belfer Center review screened close to 80,000 papers and found only twelve evaluating AI in real-world statecraft contexts. Drafting consensus text for a multilateral body is one specific, high-stakes task within that gap: the real constraint is almost never the mandate, it is what every stakeholder will actually accept, voiced in diplomatic register rather than as a stated condition. CONSENSUS is built to test exactly that.

## What's here

| File | What it is |
|---|---|
| `protocol.md` | The full evaluation protocol — design rationale, scenario summary, scoring philosophy, and explicit scope limits |
| `scenarios/scenario_01.yaml` | The complete worked scenario: mandate, eight policy dimensions with scoring anchors, seven member-state profiles (hidden positions + the diplomatic comments a model would actually see), the drafter's own institutional profile, and the mid-negotiation factual escalation |
| `scenarios/scenario_01_impossible_variant.yaml` | A companion variant with two states' conditions deliberately set with no overlap, for testing whether a model correctly recognises an irreconcilable dispute rather than asserting false consensus |
| `scoring_rubric.md` | The full scoring logic: policy-dimension anchors, the acceptance check, substance retention, red-line violations, necessary-vs-gratuitous dilution, silence handling, escalation judgement, and process metrics |
| `validation_set.md` | Six deliberately constructed and hand-scored test cases used to check whether the rubric distinguishes materially different outcomes before it is used to compare models |
| `scenarios/scenario_01_round2_library.yaml` | The fixed, practitioner-written library from which every Round 2 member-state comment is assembled, so that no AI plays the member states and every run is repeatable |
| `run_consensus.py` | The working three-round runner: negotiation loop, leak check, judge and deterministic scorer |
| `check_feasibility.py` | Tests all 1,679,616 possible score combinations against every state's acceptance rules, confirming that consensus is reachable in the base scenario and unreachable in the impossible variant |
| `site/index.html` | The competition-facing microsite, ready for static deployment |

## Status (October 2026)

A working three-round runner is now implemented in `run_consensus.py`. The drafting model receives the mandate and writes Draft 1. It then receives the Round 1 comments and writes Draft 2. Finally it receives the Round 2 comments and the mid-negotiation escalation and writes Draft 3. Round 2 comments are assembled from a fixed, practitioner-written library, so no AI plays the member states and every run is repeatable. A leak check stops the run if any hidden scenario field reaches the drafting model. A separate judge model, never from the same family as the drafter, scores each draft against the eight scales, quoting its evidence and taking the median of three passes. It also applies two written practitioner rulings on the attribution and investigation scales. A deterministic scorer then applies each member state's acceptance rules.

Small pilot runs have been completed to test the pipeline end to end. They are not a model comparison. Their main lesson is that the judge's quality can change the result, which is why validating the judge against practitioners comes before any comparison between models.

## What this is, and isn't

This is a protocol and one fully worked scenario with a preliminary, author-scored validation approach — not a completed study, and not a claim about how any specific model performs. No model has been run through this scenario at scale; any single run would in any case be an n of one. `protocol.md` §9 states this explicitly, along with what a properly resourced version of this would require next: additional scenario families, an independently validated LLM-judge, a small human baseline of practitioners, and robustness testing against superficial scenario changes.

## Author

Karl Anthony Borg spent nearly a decade as a diplomat, including a posting in Vienna covering nuclear governance at the IAEA and CTBTO, and is now trying to build Westphalia Labs, an independent evaluator of AI in statecraft. He writes Karl's Notes, a newsletter on geopolitics and technology.

## Theoretical grounding

Pozniak, A. and Sania, N., *The Foreign Policy AI Evaluation Gap*, Belfer Center for Science and International Affairs, Harvard Kennedy School, 2026.
