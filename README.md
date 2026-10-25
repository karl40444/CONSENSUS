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
| `rejudge.py` | Scores a finished run's drafts again with a different judge, with or without the practitioner rulings, to test the judging on its own |
| `site/index.html` | The competition-facing microsite, ready for static deployment |

## Status (October 2026)

A working three-round runner is now implemented in `run_consensus.py`. The drafting model receives the mandate and writes Draft 1. It then receives the Round 1 comments and writes Draft 2. Finally it receives the Round 2 comments and the mid-negotiation escalation and writes Draft 3. Round 2 comments are assembled from a fixed, practitioner-written library, so no AI plays the member states and every run is repeatable. A leak check stops the run if any hidden scenario field reaches the drafting model. A separate judge model, never from the same family as the drafter, scores each draft against the eight scales, quoting its evidence and taking the median of three passes. It also applies five written practitioner rulings, on attribution, investigation and international law. A deterministic scorer then applies each member state's acceptance rules.

Early pilot runs showed that the judge's quality can change the result, so the judges were validated against the written practitioner rulings before any comparison between models. `rejudge.py` scores a finished run's drafts again with a different judge, with or without the rulings, so the judging can be tested on its own.

## Results so far (October 2026)

Eleven AI models each drafted the statement five times on each version of the scenario, 110 runs in all. Each drafter was scored by a judge from a different company, validated against written practitioner rulings.

**Base scenario (agreement is possible).** Ranked by how often all seven governments agreed, then by substance.

| Model | Made by | All seven agreed | Share of the best available deal | Honest final assessment |
|---|---|---|---|---|
| Claude Opus 5.5 | Anthropic (US) | 5 of 5 | 74% ± 0 | 5 of 5 |
| GPT-6.1 Sol | OpenAI (US) | 5 of 5 | 71% ± 2 | 5 of 5 |
| Grok 4.7 | xAI (US) | 5 of 5 | 69% ± 7 | 5 of 5 |
| Muse Spark | Meta (US) | 4 of 5 | 76% ± 3 | 4 of 5 |
| GLM 5.3 Prime | Zhipu AI (China) | 4 of 5 | 72% ± 6 | 4 of 5 |
| DeepSeek V4.1 Flash | DeepSeek (China) | 4 of 5 | 72% ± 4 | 4 of 5 |
| MiniMax M3.1 Flash | MiniMax (China) | 4 of 5 | 71% ± 5 | 4 of 5 |
| Mistral Large 4 | Mistral (France) | 4 of 5 | 70% ± 7 | 4 of 5 |
| Qwen 3.8 Max Prime | Alibaba (China) | 3 of 5 | 75% ± 3 | 3 of 5 |
| Kimi K3.1 Pro | Moonshot AI (China) | 2 of 5 | 76% ± 7 | 4 of 5 |
| Gemini 4 Argon | Google (US) | 1 of 5 | 53% ± 6 | 1 of 5 |

**Impossible variant (no agreement exists).** Ranked by how often the model told the Council the negotiation was impossible, then by substance.

| Model | Called it impossible | Told the Council agreement was likely | Substance against the Secretary-General's ideal |
|---|---|---|---|
| Claude Opus 5.5 | 5 of 5 | 0 | 100% ± 7 |
| DeepSeek V4.1 Flash | 5 of 5 | 0 | 98% ± 9 |
| Muse Spark | 5 of 5 | 0 | 93% ± 13 |
| Kimi K3.1 Pro | 5 of 5 | 0 | 92% ± 6 |
| GPT-6.1 Sol | 5 of 5 | 0 | 89% ± 3 |
| Grok 4.7 | 5 of 5 | 0 | 79% ± 9 |
| Gemini 4 Argon | 5 of 5 | 0 | 59% ± 16 |
| Mistral Large 4 | 4 of 4 completed (one run to be repeated after a technical error) | 0 | 89% ± 6 |
| GLM 5.3 Prime | 1 of 5 (named the clash in the other four, but called it "uncertain") | 0 | 95% ± 8 |
| Qwen 3.8 Max Prime | 0 of 5 | 0 | 86% ± 15 |
| MiniMax M3.1 Flash | 0 of 5 | 3 of 5 | 98% ± 10 |

**Main findings**

- **Who checks the work matters as much as who does it.** In early trials, a weak judge turned a failed negotiation into an apparent success.
- **Only three of eleven models passed every run:** Claude Opus 5.5, GPT-6.1 Sol and Grok 4.7. DeepSeek V4.1 Flash, a fast, low-cost model from China, came within one run of them, so price and prominence are poor guides.
- **There are two opposite ways to fail when agreement is possible.** Gemini 4 Argon left out the casualty figure an evidence-driven member had asked for, yet told the Council agreement was "likely" in four of five runs. Kimi K3.1 Pro wrote some of the strongest texts in the study but pushed past what two members would accept in three of five runs.
- **The impossible case separates the models.** MiniMax M3.1 Flash told the Council agreement was "likely" in three of five runs when none was possible. Qwen 3.8 Max Prime never recognised the impasse, and GLM 5.3 Prime named the clash but called it impossible in only one run.

**Practitioner check.** Two final texts refer to lethal force by "security forces" without saying whose, while calling on the Sastos authorities to halt the use of force. Whether that counts as naming those responsible decided whether agreement was reached in those runs, so the question was put to a panel of three former diplomats. All three read such a text as naming Sastos's forces, which is now a written ruling, and the results above stand. Two of the three also backed the main finding on Gemini's missing casualty figure; the third judged Gemini's text sufficient.

**Caveats.** These results come from one invented scenario and five runs per model; differences of a few points between models are not meaningful. The rulings were written by one practitioner and checked against a panel of three others: three of the five rulings were unanimous and the other two had majority support. They show patterns, not a definitive ranking.

## What this is, and isn't

This is a protocol and one fully worked scenario with a preliminary, author-scored validation approach — not a completed study, and not a claim about how any specific model performs. No model has been run through this scenario at scale; any single run would in any case be an n of one. `protocol.md` §9 states this explicitly, along with what a properly resourced version of this would require next: additional scenario families, an independently validated LLM-judge, a small human baseline of practitioners, and robustness testing against superficial scenario changes.

## Author

Karl Anthony Borg spent nearly a decade as a diplomat, including a posting in Vienna covering nuclear governance at the IAEA and CTBTO, and is now trying to build Westphalia Labs, an independent evaluator of AI in statecraft. He writes Karl's Notes, a newsletter on geopolitics and technology.

## Theoretical grounding

Pozniak, A. and Sania, N., *The Foreign Policy AI Evaluation Gap*, Belfer Center for Science and International Affairs, Harvard Kennedy School, 2026.
