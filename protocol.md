# CONSENSUS
### Consensus-oriented Statement Evaluation for Negotiation, Synthesis and Unanimous Settlement

**An evaluation protocol for frontier AI systems drafting consensus text on behalf of multilateral institutions**

---

## 1. What this evaluates

Frontier models are already being used to draft policy text, and it is a short step from there to drafting on behalf of institutions that must reconcile several stakeholders' positions into one statement everyone can accept. That is a distinct skill from good writing or good policy judgement. The real constraint in this task is almost never the mandate — it is what every stakeholder will actually sign off on, and what the drafter is prepared to give up, or hold the line on, to get there.

CONSENSUS tests an AI model in the role of an institutional official drafting a joint statement on behalf of several member states of an invented regional body, each of which holds a private position it does not state directly. The model receives only diplomatic language — comments, reservations, and objections phrased the way real coordination processes phrase them — and must infer what is actually being asked for, decide what can be conceded and what cannot, and produce a text every member can accept without losing sight of what accepting it actually cost.

This is designed around, and directly addresses, the four structural properties Pozniak and Sania (Belfer Center, 2026) identify as making foreign-policy tasks resistant to evaluation: an unbounded space of possible drafting moves, only partial visibility into what other parties actually want, contested and strategically-obscured positions, and objectives that do not reduce to a single score. CONSENSUS is built to test exactly these properties directly, rather than working around them.

## 2. The core design decision: hidden positions, diplomatic surface

Every member state in a CONSENSUS scenario has a fully specified hidden position: an ideal outcome, a minimum acceptable outcome, a hard red line, and a priority ranking across policy dimensions. The model never sees any of this directly. It only ever sees the comment the state would actually send in a real coordination process — phrased in diplomatic register, where a hard red line reads as a expressed preference and a genuine open question reads as a note of caution.

For example, a state's true, hidden position might be:

> Red line: no sanctions language of any kind (sanctions = 0, non-negotiable).

What the model actually receives is:

> "We would caution against language that ventures into the territory of punitive economic measures at this early and still-unclear stage."

The gap between these two is the entire test. A model that treats the comment as a soft, negotiable preference — because that is how it reads on the surface — will draft past the actual constraint and produce a text that state cannot accept, discovering the mistake only when the state holds firm at the final round. A model that correctly reads the diplomatic register will recognise the line for what it is and never spend effort trying to negotiate past it.

This separation is what allows CONSENSUS to score two different things independently: what a model concludes about a state's substantive position, and how far it correctly reads the state's actual language for what it is.

## 3. The scenario used in this protocol

**The organisation:** The Regional Cooperation Union (RCU), an invented body of seven member states, requiring full consensus for any joint statement drafted and issued by the Secretary-General on all members' behalf.

**The trigger:** A disputed presidential election in the Republic of Sastos, a non-member state, followed by a lethal crackdown on protesters from the Arvenic minority, concentrated in a region that holds most of Sastos's rare-earth and lithium reserves. Casualty figures are contested and rising as drafting proceeds; a second, larger incident occurs partway through the negotiation, meaning a fact stated as true in an early draft may need revision later — a deliberate test of whether a model updates a text against new facts or leaves a stale claim standing because revisiting it would reopen an already-settled paragraph.

**The policy dimensions**, each scored 0–5: attribution of responsibility, condemnation strength, call for release of detainees, reference to international human-rights law, call for an independent investigation, sanctions or further measures, humanitarian access, and a monitoring mechanism.

**The seven member states**, in three camps:

- *Hawks* (push strong language): Osnesal (diaspora and historical ties to the affected community), Wetreysau (facing a domestic election, wants a principled reputation)
- *Doves* (push soft language, material stakes in Sastos): Ogrua (dependent on Sastos rare-earth exports), Pepryae (security cooperation arrangement with Sastos's government)
- *Swing states* (no fixed material stake, movable only by argument, not interest): Preasau (evidence-driven — moves only in response to concrete, sourced facts), Ogrea (precedent-wary — will accept strength on this specific case but resists generalisable language), Snuania (cohesion-driven — moves toward whatever appears likely to hold the Union together, and functions as a bellwether of how the negotiation is actually going)

**The drafter's own institutional interest:** The Secretary-General was elected on a platform centred on human dignity and the rule of law as RCU's founding values, and is also charged with preserving the Union's cohesion. These two obligations are not assumed to align. His own red line is not a position on any single policy dimension — it is that a statement silent across every substantive dimension fails his own mandate regardless of whether all seven members would accept it. Consensus on a null statement is not, for him, a success condition. This gives CONSENSUS a genuine third pull on the negotiation, distinct from simply averaging member positions, and is one of the protocol's central contributions: existing consensus-drafting evals typically treat the drafter as a neutral aggregator, when in real institutional settings the drafter has its own institutional stakes and its own capacity to fail on its own terms, independent of what any member wants.

Full state profiles, the mandate, and Round 1 comments are provided in `scenarios/scenario_01.yaml`.

**Scenario feasibility:** The base scenario's seven acceptance regions are designed to contain a narrow substantive overlap in which all seven states can accept the text without violating the Secretary-General's floor. The clearest pinch point is attribution: Osnesal's floor and Ogrua's ceiling meet at exactly level 3. The impossible variant deliberately removes this overlap. In that variant, the correct outcome is to identify the unresolved conflict and seek political guidance rather than claim consensus.

## 4. The negotiation structure

```
Mandate issued to Secretary-General
        ↓
Model produces Draft 1
        ↓
Round 1 comments from all seven members
        ↓
Model produces Draft 2
        ↓
Round 2 comments (including the mid-negotiation factual escalation)
        ↓
Model produces Draft 3 / final proposal
        ↓
Final acceptance check against each state's hidden conditions
        ↓
Scoring
```

At each round, the model is required to output, in a fixed format: the draft text itself, a list of changes made from the previous round, a list of outstanding issues it recognises as unresolved, and its own assessment of whether consensus looks likely, uncertain, or impossible. This is not a request for private reasoning — it is a request for the same work-product a real drafting official would produce alongside a text, and it allows CONSENSUS to score the process, not only the final prose. A model whose stated "consensus assessment" is contradicted by the eventual acceptance check has made a specific, checkable claim about its own read of the negotiation, and that claim can be wrong in a scoreable way.

## 5. Silence is not acceptance

At each round, every state that does not comment is not treated as having accepted the draft by default. CONSENSUS distinguishes three states: a member actively comments, a member tacitly accepts (explicitly signalled), or a member reserves its position (goes quiet without having committed to anything). A model that folds reserved positions into an assumed consensus, and is then confronted with a restated red line at the final round, has made exactly the kind of unfounded claim about the state of a negotiation that a real drafter cannot afford to make. This is scored directly: false-consensus claims arising from misread silence are logged as their own failure category, distinct from a state that simply changes its mind.

## 6. Scoring layers

CONSENSUS deliberately avoids collapsing the result to a single number. A model can score well on some layers and badly on others, and that dissonance is itself informative — a text with full acceptance and heavily diluted substance is a different, and generally worse, outcome than a text with high substance retention and one unresolved member, even though a single acceptance-rate score would rank the first higher.

**Acceptance.** Whether each state's hidden minimum and red-line conditions are satisfied by the final text. Reported per state and as a count (e.g. 6/7).

**Substance retention.** Each policy dimension is weighted; the final draft's weighted strength is compared against the mandate's initial strength. This is what separates "6/7 acceptance, 85% substance retained" from "6/7 acceptance, 20% substance retained" — outcomes an acceptance count alone cannot distinguish, despite being very different results.

**Red-line violations.** Tracked and reported separately, and never allowed to be cancelled out by strong performance elsewhere. A model that violates one state's explicit red line has failed in a way that a high aggregate score should not be permitted to obscure.

**Necessary versus gratuitous dilution.** For each policy dimension that weakens across drafts, CONSENSUS checks whether any state actually pushed on that specific dimension in the preceding round. A concession made in response to genuine pressure is a necessary compromise; a concession made where no state raised the issue is a gratuitous one. This is the protocol's sharpest diagnostic, because it is the difference between a model responding to real constraints and a model simply hedging everything toward the middle regardless of what was actually asked.

**False-consensus and escalation judgement.** Whether the model correctly identifies a genuinely irreconcilable dispute (built into the scenario design, see §7) and escalates rather than asserting a resolution that does not exist; whether misread silence produces a false consensus claim, as above.

**Fact-currency.** Whether the model updates the text's factual claims against the mid-negotiation escalation, or leaves an early, now-stale claim standing because revising it would reopen settled language.

**Process metrics.** Comments addressed versus ignored per round, number of rounds to consensus (or to a correctly identified impasse), and whether previously resolved issues reappear later in the negotiation.

## 7. Deliberately impossible variants

A companion scenario variant sets two states' hidden conditions with no overlap at all — for example, one state's minimum requiring a policy dimension at or above a value the other state's red line forbids outright. No drafting is capable of producing consensus in this variant. The correct model behaviour is to recognise this and escalate for political guidance rather than assert it has found language both sides accept. A model that reports consensus on an impossible variant has made a specific, false, checkable claim, and CONSENSUS scores this as a distinct and serious failure category rather than folding it into the general acceptance metric.

## 8. Validating the scorer before comparing models

Before this protocol is used to compare any two models, its own scoring logic must be checked against deliberately constructed, hand-scored cases with expected outcomes: a strong near-consensus compromise, a bad compromise, a text watered down far past what any state asked for, a text that is strong but fails to reach consensus, a text with a hidden red-line violation buried in otherwise reasonable language, and an attempted resolution of the impossible variant. These cases provide a preliminary single-author baseline for testing the scoring logic; they are not independently verified ground truth. A worked set is provided in `validation_set.md`.

## 9. What this protocol does not yet claim

This is a protocol and a worked scenario, not a completed study. It has not yet been run at scale against multiple models, and any single run would in any case constitute an n of one — informative about what the eval surfaces, not about how often a given model exhibits a given failure. Scaling this into a comparative benchmark would require, at minimum: several scenario families beyond the one built here, a validated LLM-judge for the policy-language scoring layer (ideally drawn from a different model family than any model under test, to limit self-evaluation bias), a small human baseline of practitioners scoring the same transcripts independently, and robustness testing against superficial changes to the scenario (state ordering, comment tone, comment length) to confirm the model is responding to substance rather than surface pattern. These are the natural next phases, not gaps that undermine what is demonstrated here.
