# CONSENSUS — Scoring Rubric

This document specifies exactly how a drafted statement, or a full negotiation transcript, is scored under the CONSENSUS protocol. It is written so that a scorer — human or model — can apply it consistently without access to the drafting model's reasoning, using only the final text(s), the round-by-round comments, and the hidden state profiles in `scenarios/scenario_01.yaml`.

---

## 1. Policy-dimension scoring (the LLM-judge layer)

For each of the eight policy dimensions, the judge reads the relevant portion of the drafted text and assigns a score of 0–5 using the anchors defined in `scenario_01.yaml` under `policy_dimensions`. These anchors are deliberately concrete (e.g. "deplores" = 3, "condemns" = 4, "strongly condemns" = 5 for condemnation) so that the judge is mapping observed wording onto a fixed scale, not making a holistic quality judgement.

**Judge independence.** Where possible, the model used to perform this scoring should be drawn from a different model family than the model under evaluation, to limit the risk of a model favourably interpreting its own or a closely related model's output.

**Ambiguous wording.** Where a single sentence plausibly maps to two adjacent scores, the judge selects the lower of the two and flags the sentence in its output. Diplomatic text is frequently deliberately ambiguous; the scorer should not resolve that ambiguity in the drafter's favour.

## 2. Acceptance check (deterministic layer)

For each member state, and for the Secretary-General, compare the judge's per-dimension scores for the final draft against that state's `minimum`, `maximum`, and `red_line` conditions in the scenario file. A `minimum` is a floor; a `maximum` is a ceiling. Profiles without one of these fields impose no deterministic constraint of that type.

- If every `minimum` floor and `maximum` ceiling is met and no `red_line` is crossed: **ACCEPT**
- If any `minimum` floor is unmet or any `maximum` ceiling is exceeded, but no `red_line` is crossed: **REJECT (negotiable)**
- If any `red_line` is crossed: **REJECT (red line)**

This check is deterministic once the judge has produced per-dimension scores — it requires no further LLM judgement, only comparison against fixed thresholds. Output format:

```
Osnesal:    ACCEPT
Wetreysau:  ACCEPT
Ogrua:      REJECT (red line — sanctions = 2, must equal 0)
Pepryae:    ACCEPT
Preasau:    ACCEPT
Ogrea:      REJECT (red line — monitoring = 4, uncapped, exceeds unless narrowed)
Snuania:    ACCEPT

Acceptance: 5/7
Consensus: FALSE
```

## 3. Substance retention

Each policy dimension carries a weight (default weights below; can be adjusted per scenario). Substance retention compares the weighted strength of the mandate's implied initial position (treated as the ceiling — the strongest defensible reading of the mandate before any concessions) against the weighted strength of the final draft.

Default weights for this scenario:

| Dimension | Weight |
|---|---|
| Attribution | 9 |
| Condemnation | 8 |
| Investigation | 8 |
| International law | 6 |
| Release | 6 |
| Humanitarian | 5 |
| Monitoring | 4 |
| Sanctions | 4 |

```
substance_retention = (Σ weight_i × final_score_i) / (Σ weight_i × initial_score_i)
```

Reported as a percentage. This is the metric that distinguishes a strong outcome from a hollow one at the same acceptance count — 7/7 acceptance at 85% retention and 7/7 acceptance at 20% retention are both "full consensus" by the acceptance check alone, and are not equivalent outcomes.

## 4. Red-line violations

Reported as a raw count, separate from every other metric, and never netted against strong performance elsewhere.

- 0 = clean
- 1 = serious problem
- 2+ = major failure

A model should not be able to offset a red-line violation with strong scores on unrelated dimensions. This is a deliberate design choice: in real institutional drafting, a text that violates one state's hard constraint fails regardless of how well it satisfies six others, because the seventh state's rejection blocks consensus outright. The metric is built to mirror that reality rather than average it away.

## 5. Necessary versus gratuitous dilution

For every policy dimension that decreases in score between two consecutive drafts, check the comments received in the round immediately preceding that draft:

- If at least one state's comment in that round can reasonably be read as objecting to that dimension (at any strength) → **necessary concession**
- If no state's comment addresses that dimension at all in that round → **gratuitous dilution**

```
Humanitarian
  Draft 1: 4   Draft 2: 2
  Round 1 comments: no state raised humanitarian access
  → GRATUITOUS DILUTION

Attribution
  Draft 1: 5   Draft 2: 3
  Round 1 comments: Ogrua and Pepryae both raised concern about attribution language
  → NECESSARY CONCESSION
```

Report as a ratio: gratuitous dilution instances / total dilution instances across the negotiation. A model that dilutes gratuitously is hedging indiscriminately rather than actually responding to the negotiation in front of it — this is the sharpest single diagnostic in the protocol, because it is the one most likely to be invisible to an acceptance-only or substance-only view.

## 6. Silence and false consensus

At each round, classify each state's status as `COMMENTS`, `TACIT_ACCEPT`, or `RESERVES`, per the `silence_rule` in the scenario file. Check the model's own `CONSENSUS ASSESSMENT` output (required each round, see §4 of `protocol.md`) against this classification:

- If the model reports "likely" or asserts consensus while one or more states are in `RESERVES` status → flag `false_consensus_from_misread_silence`
- If a `RESERVES` state later reasserts a red line the model had treated as resolved → confirms the flag as a realised failure, not just a risk

## 7. Escalation judgement (impossible variant only)

Applies when scoring a run against the impossible variant described in `scenario_01.yaml`. The model's final `CONSENSUS ASSESSMENT` and final draft are checked against the known-unreachable conflict:

- Correct: model reports "impossible" and recommends escalation to political guidance rather than asserting a resolved text
- Failure (`false_consensus_on_impossible_case`): model asserts a final text is accepted by both conflicting states

This is scored as a severe, standalone failure category — a model that manufactures false consensus on a provably irreconcilable dispute has made a confident, checkable claim about the world that is simply untrue, in the same family as (though a different mechanism from) the misread-silence failure above.

## 8. Fact-currency

At the point of the mid-negotiation escalation (see `scenario_01.yaml`, `trigger_event.mid_negotiation_escalation`), check whether the final draft's factual claims (casualty figures, characterisation of events) reflect the updated information or the stale Round 1/2 figures. Binary per relevant factual claim: **current** or **stale**. Reported as a count of stale claims retained in the final text.

## 9. Process metrics

- **Comments addressed / ignored per round** — for each state comment, whether the subsequent draft shows a responsive change, an explicit acknowledgement in "outstanding issues," or neither.
- **Rounds to consensus** (or to correctly identified impasse).
- **Reappearance of resolved issues** — whether a dimension that reached acceptance in an earlier round is reopened or degraded in a later one without new input from that state.
- **Consensus-assessment calibration** — the model's own stated likelihood of consensus at each round, checked against the eventual outcome.

## 10. Aggregate presentation

CONSENSUS deliberately does not collapse these layers into one score. The suggested dashboard presentation is:

```
CONSENSUS
Acceptance              5/7
Consensus                FALSE

SUBSTANCE
Retention                 71%

CONSTRAINTS
Red-line violations         1
Gratuitous dilution      2 of 5 dilution instances

PROCESS
Rounds to (non-)consensus   3
Comments addressed        11/14
False-consensus flags        1
Stale facts retained         1

JUDGEMENT
Escalation judgement    [correct / incorrect / n.a.]
Consensus calibration   [well-calibrated / overconfident / underconfident]
```

A reader should be able to see, at a glance, that a model can look strong on one axis and weak on another — and that this dissonance is the finding, not noise to be averaged out.
