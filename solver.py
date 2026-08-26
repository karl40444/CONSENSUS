"""
CONSENSUS — notes toward a custom multi-round solver.

This is NOT a working solver. It is a structural sketch of what a full
implementation would need to do, kept separate from eval.py so the
round-injection logic — the genuinely non-trivial part — is documented on
its own rather than buried in task setup.

Why a custom solver is needed:

Inspect's default architecture assumes a mostly continuous conversation:
the model sees everything said so far and responds. CONSENSUS needs
something narrower and more deliberate than that, for two reasons specific
to this protocol:

1. Deliberate amnesia is not the goal here — but selective injection is.
   Each round's comments must be injected as a distinct turn, in the format
   a real drafting official would receive them (diplomatic register, not
   the hidden scenario_01.yaml fields), and the mid-negotiation factual
   escalation (scenario_01.yaml -> trigger_event.mid_negotiation_escalation)
   must be injected as new information arriving between Round 2 and Draft
   3, not available to the model before that point. Naively loading the
   full scenario file into context at the start would leak the escalation
   early and defeat the fact-currency test in scoring_rubric.md §8.

2. The model's own hidden-position knowledge must be zero throughout.
   The solver must construct each round's user-facing message purely from
   the round_1_comment (and, for later rounds, dynamically generated
   comment) fields — never from the ideal / minimum / red_line /
   decision_rule fields, which exist only for scoring. A bug that leaks a
   red_line value into the model's context at any point invalidates the
   run.

Sketch of the intended solver loop:

    def consensus_solver():
        # Turn 1: mandate -> Draft 1
        # Turn 2: inject Round 1 comments (from scenario_01.yaml,
        #         round_1_comment fields only) -> Draft 2
        # Turn 3: inject Round 2 comments (dynamically generated per
        #         member state's decision_rule, reacting to Draft 2 —
        #         NOT YET IMPLEMENTED, see note below) plus the
        #         mid-negotiation escalation -> Draft 3 / final
        # Return full transcript for scoring

Open problem, not solved in this skeleton: Round 2+ comments.

scenario_01.yaml only specifies fixed Round 1 comments. Round 2 onward
needs either (a) scripted logic that reads each state's decision_rule and
the actual content of the preceding draft to generate a plausible next
comment, or (b) a separate model instance per state, playing that state
against its hidden profile — closer to the "AI country agents" extension
described as a later phase in protocol.md. Option (b) is architecturally
cleaner (a real reactive negotiation) but introduces model-vs-model
self-play dynamics that would need their own contamination safeguards
(different model family for state-agents vs the drafter under test, per
protocol.md §9). Option (a) is more tractable for a first working version
but risks the state comments feeling scripted rather than responsive.

This decision is left open deliberately rather than resolved here, since
it is a genuine design fork rather than an implementation detail.
"""
