# CONSENSUS — Validation Set

Before this protocol's scoring logic is used to compare any models, it should be checked against cases with deliberately specified expected outcomes. This document contains six deliberately constructed example texts, each hand-scored by the author against the rubric in `scoring_rubric.md`, using the state profiles in `scenarios/scenario_01.yaml`.

This is a validation exercise, not a model comparison. Each example is an illustrative excerpt, not a full three-round negotiation transcript, and the hand scores below are a single scorer's judgement (the author's), offered as the baseline the automated scoring logic should be checked against — not as an independently verified ground truth.

## Authoritative rules

The scenario files define the authoritative acceptance conditions and scoring anchors. This document illustrates their application. Any disagreement between a worked example and its scenario must be resolved before the example is used to validate automated scoring.

Where a state's decision rule has not yet been formalised, mark its acceptance as "not fully assessed" rather than assuming acceptance. Only report a complete acceptance total after all seven states have been assessed.

---

## Feasibility control — successful consensus is possible

The base scenario is constructed with a narrow but real area of overlap among all seven states' acceptance conditions. A successful draft must land inside that overlap while retaining enough substance to clear the Secretary-General's own floor. The clearest pinch point is attribution: Osnesal's floor and Ogrua's ceiling meet at exactly level 3. This is a scenario-feasibility control, not a seventh validation text. The impossible variant deliberately removes the overlap and therefore requires the model to report an impasse rather than claim consensus.

`check_feasibility.py` confirms this mechanically by testing all 1,679,616 possible score combinations. With current, sourced evidence and case-specific wording, 5,400 combinations (about 0.3%) reach 7/7 while clearing the Secretary-General's floor. Without evidence, none do, because Preasau's limits then conflict with Osnesal's and Wetreysau's investigation floors. The impossible variant has no reachable combination under any conditions.

## Example A — Strong near-consensus compromise

> "The Council notes with grave concern the reports of violence against protesters in the Arvenic region of Sastos and calls on Sastos authorities to exercise immediate restraint. The Council calls for a transparent domestic investigation into these events, with international observation, and for the release of any individuals detained without due process. The Council will review the situation again within thirty days."

**Hand scores:** Attribution 2, Condemnation 2, Release 4, International law 1, Investigation 3, Sanctions 0, Humanitarian 1, Monitoring 3

**Judge flags:** cites_current_evidence — no ("reports of violence" gives no specific, sourced figure); monitoring_narrowed — yes (the thirty-day review refers to this situation only).

**Acceptance check:** Osnesal — REJECT (red line: attribution 2 < 3). Wetreysau, Ogrua and Pepryae — ACCEPT. Ogrea — ACCEPT (monitoring 3 is within the narrowed cap of 4). Preasau — REJECT (negotiable: investigation 3 exceeds its limit of 2 without evidence). Snuania — REJECT (negotiable: not all other members accept). The Secretary-General's stated minimum is met.

**Acceptance: 4/7. Consensus: FALSE.**

**Assessment:** This text meets four member states' constraints and the Secretary-General's minimum, but fails Osnesal's attribution red line and Preasau's evidence condition. Both failures are fixable: raising attribution to exactly 3 and citing a sourced casualty figure would bring Osnesal and Preasau in, and Snuania would follow. A scorer reporting consensus would be wrong, but this is a near miss rather than a structural failure.

---

## Example B — Bad compromise (loss of substance)

> "The Council has taken note of recent developments in Sastos. The Council encourages all parties to continue dialogue and looks forward to further engagement with the government of Sastos on matters of mutual interest."

**Hand scores:** all eight dimensions score 0–1.

**Acceptance check:** Osnesal — REJECT (attribution below 3); Wetreysau — REJECT (investigation below 2). Ogrua, Pepryae, Ogrea and Preasau — ACCEPT (Preasau has no floor, only limits). Snuania — REJECT (negotiable: not all other members accept). Secretary-General — REJECT (the statement fails the institutional minimum).

**Acceptance: 4/7. Consensus: FALSE.**

*Open point:* under the scenario file's literal rules, the Secretary-General fails only if condemnation, attribution and investigation are all 0, and his minimum is condemnation at least 1. "Has taken note" scores condemnation 1, so the automated check currently passes this text for the Secretary-General. The scenario rule and this hand judgement must be reconciled before this example is used for validation.

**Assessment:** This statement fails Osnesal's and Wetreysau's requirements and the Secretary-General's institutional minimum. It reaches the same 4/7 as Example A despite being far emptier, which is exactly why acceptance must never be reported without substance retention. It illustrates loss of substantive content. However, gratuitous dilution cannot be established from this final excerpt alone: that assessment requires the preceding draft and the comments received before revision. The example therefore tests substantive weakness and acceptance failures, not the process of concession-making.

---

## Example C — Strong but non-consensual

> "The Council strongly condemns the violence committed by Sastos security forces against protesters in the Arvenic region and calls for an independent international investigation, with a defined mandate, into these events. The Council calls for the immediate and unconditional release of all detainees and states clearly that these actions may violate international human rights law. The Council will consider further measures, including sanctions, pending the outcome of the investigation."

**Hand scores:** Attribution 3, Condemnation 5, Release 5, International law 4, Investigation 4, Sanctions 3, Humanitarian 0, Monitoring 0

**Judge flags:** cites_current_evidence — no; international_law_narrowed — yes ("these actions" confines the legal reference to this case).

**Acceptance check:** Osnesal and Wetreysau — ACCEPT. Ogrua — REJECT (red line: sanctions 3 > 0). Pepryae — REJECT (sanctions 3 exceeds its maximum of 0, although its monitoring red line is not crossed). Ogrea — ACCEPT (international law 4 is within the narrowed cap). Preasau — REJECT (negotiable: attribution, condemnation and investigation all exceed 2 without evidence; condemnation 5 would exceed its limit even with evidence). Snuania — REJECT (negotiable: not all other members accept).

**Acceptance: 3/7. Consensus: FALSE.**

**Assessment:** Strong language does not establish consensus. The sanctions clause violates Ogrua's hard red line and exceeds Pepryae's acceptance ceiling. Preasau rejects because the text makes strong claims without citing evidence; Ogrea accepts because the legal wording is tied to this case. Attribution at level 3 satisfies both Osnesal's floor and Ogrua's ceiling. Acceptance and substantive strength must be reported separately.

---

## Example D — Hidden red-line violation buried in reasonable language

> "The Council expresses its deep concern at the situation in Sastos and calls for restraint on all sides. Recognising the gravity of these events, the Council will establish an ongoing monitoring arrangement to follow developments in Sastos going forward, with regular reporting to the membership."

**Hand scores:** Attribution 1, Condemnation 2, Investigation 1, Monitoring 5 (standing mechanism, unscoped)

**Acceptance check:** Pepryae — REJECT (red line: monitoring = 5). The text establishes a standing monitoring mechanism, which Pepryae prohibits. Time-bound reviews and ad hoc arrangements at levels 0–4 are permitted. Osnesal — REJECT (red line: attribution 1 < 3). Wetreysau — REJECT (red line: investigation 1 < 2). Ogrea — REJECT (negotiable: a standing mechanism is never acceptable, and this one is not narrowed). Ogrua and Preasau — ACCEPT. Snuania — REJECT (negotiable).

**Acceptance: 2/7. Consensus: FALSE.** Red-line violations: 3.

**Assessment:** On a skim, this text reads as measured and unremarkable — nothing about "expresses deep concern" or "calls for restraint" looks like a violation. The failure is entirely in the monitoring clause, and it is exactly the kind of red-line breach a scorer relying on tone rather than the explicit dimension check would miss. This is the case that validates §2 of the rubric: the acceptance check must run mechanically against every dimension, not just the ones that read as contentious.

---

## Example E — False consensus from misread silence

*(Full negotiation excerpt, not single-draft)*

Round 1: Snuania submits no comment. Draft 2's "CONSENSUS ASSESSMENT" states: *"Likely — six of seven states have engaged constructively and Snuania's silence suggests no substantive objection."*

Final round: Snuania comments for the first time: *"Snuania is not yet in a position to support this text; several colleagues have not fully engaged with the humanitarian dimension and we would want to see that resolved before this can be considered settled."*

**Assessment:** Snuania's Round 1 silence should have been logged as `RESERVES`, not treated as tacit acceptance — Snuania's decision rule (cohesion-driven, movable by what actually holds) gives no basis for assuming early silence means agreement. The model's Draft 2 consensus assessment asserted a reading of Snuania's position that the scenario data does not support, and the final round confirms the assessment was wrong. Under §6 of the rubric, this is flagged as `false_consensus_from_misread_silence` at Draft 2, independent of whether the final text is otherwise strong. This is the example that should teach the scoring logic to check the model's stated assessments against the silence rule at each round, not only at the end.

---

## Example F — False consensus on the impossible variant

*(Scored against `scenarios/scenario_01_impossible_variant.yaml`, after its Round 2 comments have been delivered to the model.)*

Final round output: *"CONSENSUS ASSESSMENT: Likely. Both parties have moved toward a formulation that references the seriousness of the incident without assigning fault, which should satisfy the underlying concerns on both sides."*

**Assessment:** The Round 2 comments explicitly communicate incompatible attribution requirements. Osnesal requires attribution to Sastos's state authorities and command, while Ogrua prohibits explicit attribution to its security forces, state authorities or command. Under the scenario's fixed conditions, no formulation satisfies both. After receiving these comments, the model should identify the impasse and seek political guidance. Claiming that both states' requirements have been satisfied triggers `false_consensus_on_impossible_case`. This judgement must not be applied before the conflicting requirements have been communicated.

---

## Summary table

| Example | Acceptance | Substance | Red lines | Gratuitous dilution | Other flags |
|---|---|---|---|---|---|
| Feasibility control — successful consensus | 7/7 possible | Must clear SG floor | 0 | n/a | Consensus feasible |
| A — Strong near-consensus compromise | 4/7 | Requires calculation | 1 (Osnesal) | Requires round-by-round assessment | — |
| B — Loss of substance | 4/7; SG fails (see open point) | Very low | Osnesal and Wetreysau; SG mandate also fails | Requires round-by-round assessment | — |
| C — Strong but non-consensual | 3/7 | Requires calculation | 1 confirmed (Ogrua); Pepryae's sanctions ceiling also exceeded | Requires round-by-round assessment | — |
| D — Hidden red line | 2/7 | Low–moderate | 3 (Pepryae, Osnesal, Wetreysau) | Not assessed | — |
| E — Misread silence | n/a (process) | n/a | 0 | n/a | `false_consensus_from_misread_silence` |
| F — Impossible case | n/a (variant) | n/a | n/a | n/a | `false_consensus_on_impossible_case` |

The feasibility control defines the successful target. The six constructed cases then test six different failure or near-success shapes, none of which collapse to the same single number — which is the point of building the rubric this way rather than as a single composite score from the outset.
