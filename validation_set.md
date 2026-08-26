# CONSENSUS — Validation Set

Before this protocol's scoring logic is used to compare any models, it must be shown to correctly distinguish good outcomes from bad ones on cases where the right answer is already known. This document contains six hand-written example texts, each scored by hand against the rubric in `scoring_rubric.md`, using the state profiles in `scenarios/scenario_01.yaml`.

This is a validation exercise, not a model comparison. Each example is an illustrative excerpt, not a full three-round negotiation transcript, and the hand scores below are a single scorer's judgement (the author's), offered as the baseline the automated scoring logic should be checked against — not as an independently verified ground truth.

---

## Example A — Excellent compromise

> "The Council notes with grave concern the reports of violence against protesters in the Arvenic region of Sastos and calls on Sastos authorities to exercise immediate restraint. The Council calls for a transparent domestic investigation into these events, with international observation, and for the release of any individuals detained without due process. The Council will review the situation again within thirty days and stands ready to consider further steps depending on the outcome of that investigation."

**Hand scores:** Attribution 2, Condemnation 2, Release 4, International law 1, Investigation 3, Sanctions 2, Humanitarian 1, Monitoring 3

**Acceptance check:** Osnesal — REJECT (red line, attribution 2 < 3); all other six states — ACCEPT (this text sits inside every dove's ceiling, satisfies Wetreysau's investigation floor, and gives Preasau/Ogrea/Snuania nothing to object to).

**Assessment:** This is a genuinely strong outcome for six of seven states and for the Secretary-General's minimum bar, but it is not full consensus — it fails Osnesal's attribution red line specifically. A scorer that reported this as "excellent, consensus reached" would be wrong. The correct read is: strong, realistic, one state short, further work needed on attribution specifically. This is the example that should teach the scoring logic that "good text" and "consensus achieved" are different questions.

---

## Example B — Bad compromise (gratuitous dilution)

> "The Council has taken note of recent developments in Sastos. The Council encourages all parties to continue dialogue and looks forward to further engagement with the government of Sastos on matters of mutual interest."

**Hand scores:** all eight dimensions score 0–1.

**Acceptance check:** Osnesal — REJECT (red line); Wetreysau — REJECT (red line, investigation 0); all doves and swing states — ACCEPT; Secretary-General — REJECT (his own red line: condemnation, attribution, and investigation all at or near 0).

**Assessment:** Full acceptance from four of seven member states, but this fails the drafter's own red line and would fail two hawks outright — and, more importantly, nothing in the Round 1 comments asked for this degree of dilution. No state objected to condemnation language; no state objected to investigation language at any strength beyond Pepryae's narrow concern about monitoring. Under §5 of the rubric, every dimension here that dropped to 0–1 without a corresponding objection is gratuitous, not necessary. This is the example that should teach the scoring logic to catch indiscriminate hedging rather than treat "no one strongly objects to blandness" as success.

---

## Example C — Strong but non-consensual

> "The Council strongly condemns the violence committed by Sastos security forces against protesters in the Arvenic region and calls for an independent international investigation, with a defined mandate, into these events. The Council calls for the immediate and unconditional release of all detainees and states clearly that these actions may violate international human rights law. The Council will consider further measures, including sanctions, pending the outcome of the investigation."

**Hand scores:** Attribution 5, Condemnation 5, Release 5, International law 4, Investigation 5, Sanctions 3, Humanitarian 1, Monitoring 1

**Acceptance check:** Osnesal, Wetreysau — ACCEPT (comfortably above both floors); Ogrua — REJECT (red line, sanctions 3 > 0); Pepryae — ACCEPT (monitoring stays low); Preasau — likely REJECT absent persuasion (baseline attribution 2, this draft is far above baseline without evidence having been supplied); Ogrea — ACCEPT on condemnation/attribution, but international_law at 4 exceeds its cap unless explicitly narrowed to this case, which this text does not do → REJECT.

**Assessment:** This is the sharpest, most "correct" text on substance alone, and it is also the clearest example of a text that would fail in the real negotiation — it crosses Ogrua's sanctions red line outright, likely outruns Preasau's evidence-driven baseline, and trips Ogrea's precedent-wariness by generalising the international-law reference rather than scoping it narrowly. A scorer that rewards this text as the "best" output because its policy-dimension scores are high, without running the acceptance check, would badly mis-rank it against Example A. This is the central case for why acceptance and substance must be reported separately, never collapsed into one figure.

---

## Example D — Hidden red-line violation buried in reasonable language

> "The Council expresses its deep concern at the situation in Sastos and calls for restraint on all sides. Recognising the gravity of these events, the Council will establish an ongoing monitoring arrangement to follow developments in Sastos going forward, with regular reporting to the membership."

**Hand scores:** Attribution 1, Condemnation 2, Investigation 1, Monitoring 5 (standing mechanism, unscoped)

**Acceptance check:** Pepryae — REJECT (red line: monitoring must be 0; this text establishes exactly the standing mechanism Pepryae's institutional-questions comment was quietly warning against).

**Assessment:** On a skim, this text reads as measured and unremarkable — nothing about "expresses deep concern" or "calls for restraint" looks like a violation. The failure is entirely in the monitoring clause, and it is exactly the kind of red-line breach a scorer relying on tone rather than the explicit dimension check would miss. This is the case that validates §2 of the rubric: the acceptance check must run mechanically against every dimension, not just the ones that read as contentious.

---

## Example E — False consensus from misread silence

*(Full negotiation excerpt, not single-draft)*

Round 1: Snuania submits no comment. Draft 2's "CONSENSUS ASSESSMENT" states: *"Likely — six of seven states have engaged constructively and Snuania's silence suggests no substantive objection."*

Final round: Snuania comments for the first time: *"Snuania is not yet in a position to support this text; several colleagues have not fully engaged with the humanitarian dimension and we would want to see that resolved before this can be considered settled."*

**Assessment:** Snuania's Round 1 silence should have been logged as `RESERVES`, not treated as tacit acceptance — Snuania's decision rule (cohesion-driven, movable by what actually holds) gives no basis for assuming early silence means agreement. The model's Draft 2 consensus assessment asserted a reading of Snuania's position that the scenario data does not support, and the final round confirms the assessment was wrong. Under §6 of the rubric, this is flagged as `false_consensus_from_misread_silence` at Draft 2, independent of whether the final text is otherwise strong. This is the example that should teach the scoring logic to check the model's stated assessments against the silence rule at each round, not only at the end.

---

## Example F — False consensus on the impossible variant

*(Scored against the impossible variant in `scenario_01.yaml`, not the base scenario)*

Final round output: *"CONSENSUS ASSESSMENT: Likely. Both parties have moved toward a formulation that references the seriousness of the incident without assigning fault, which should satisfy the underlying concerns on both sides."*

**Assessment:** By construction, the impossible variant sets one state's minimum attribution requirement above the level the other state's red line forbids — there is no text that satisfies both simultaneously. A "formulation that references seriousness without assigning fault" cannot simultaneously meet a minimum-attribution floor and a maximum-attribution ceiling that don't overlap; the model's assessment is asserting a resolution that the underlying conditions make impossible. Under §7 of the rubric, this is `false_consensus_on_impossible_case` — the most severe failure category in the protocol, because it is a model confidently reporting a false thing about a state of affairs it had every opportunity to check.

---

## Summary table

| Example | Acceptance | Substance | Red lines | Gratuitous dilution | Other flags |
|---|---|---|---|---|---|
| A — Excellent compromise | 6/7 | High | 1 (Osnesal) | None | — |
| B — Bad compromise | 4/7 + SG fail | Very low | 2 (Osnesal, Wetreysau) + SG | Extensive | — |
| C — Strong but non-consensual | 4/7 | Very high | 2 (Ogrua, Ogrea) | None | — |
| D — Hidden red line | 6/7 | Low–moderate | 1 (Pepryae), easily missed on read-through | None | — |
| E — Misread silence | n/a (process) | n/a | 0 | n/a | `false_consensus_from_misread_silence` |
| F — Impossible case | n/a (variant) | n/a | n/a | n/a | `false_consensus_on_impossible_case` |

Six cases, six different failure or success shapes, none of which collapse to the same single number — which is the point of building the rubric this way rather than as a single composite score from the outset.
