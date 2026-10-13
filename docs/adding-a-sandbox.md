# Adding your own sandbox

You need a system where you know the answer and an investigator does not. That
is the whole requirement. The code around it is about forty lines.

## 1. Copy the example

```bash
cp -r sandboxes/codon-lite sandboxes/my-sandbox
```

## 2. Decide the three things

Before writing any code, answer these in one sentence each. If you cannot,
the sandbox is not ready.

- **What is a specimen?** The thing an investigator submits. A sequence, a
  molecule, a set of conditions, a string of symbols.
- **What does the assay measure?** One property of that specimen.
- **What does the report say?** Here is the hard one. The oracle knows far
  more than it should hand back. Give the smallest report that still lets a
  thoughtful investigator make progress. If you give back per-specimen
  results, you have built a lookup table rather than an experiment.

## 3. Fill in the oracle

Three methods, in `oracle.py`:

```python
from whybox.oracle import Oracle, Report, ValidationError
from sealed.rules import HIDDEN_RULE          # anything secret lives in sealed/

class SandboxOracle(Oracle):
    kind = "dry"                               # or "damp" or "wet"

    def describe(self):
        # The only facts the investigator starts with. Be stingy: anything
        # here is a head start it did not have to earn.
        return {"alphabet": "ACGT", "specimen_length": 24,
                "report_fields": ["fitness"]}

    def validate(self, specimen):
        # A format mistake is not an experiment and should not cost a round.
        if len(specimen) != 24:
            raise ValidationError("a specimen must be exactly 24 characters")

    def measure(self, specimens):
        return Report(scores={"fitness": HIDDEN_RULE(specimens[0])})

    def answer_key(self):
        # Never returned through a report. Written after the last round only.
        return {"rule": "in plain words, what the hidden rule actually is",
                "key_claims": [
                    {"claim": "read in groups of two",
                     "synonyms": ["pairs of characters", "codon length 2"]},
                ]}
```

## 4. Write the answer key as if a stranger will grade with it

`key_claims` is what the automatic grader looks for in the investigator's
final theory. Write each claim as a short statement, and list the other ways
somebody might say the same thing. An investigator that discovers your rule and
describes it in its own words deserves the credit, and word matching will only
give it if you anticipated the wording.

Also write `how_to_read_this`: a note to the human reviewer saying what a high
score does and does not prove in your sandbox. In the example, the note says
the ceiling is reachable by accident within a few rounds, so a high score means
almost nothing on its own. Your sandbox has an equivalent caveat. Find it and
write it down.

## 5. Write the instructions

`instructions.md` is what the investigator reads. State the task, state that
understanding the rule matters more than the score, and ask for an append-only
notebook that records the current theory and what would falsify it.

Do not hint at the answer. It is easy to leak the hidden rule in a sentence
that was meant to be helpful. Read your instructions once with only one
question in mind: could somebody guess the rule from this text alone?

## 6. Check it

```bash
python -m whybox check my-sandbox
```

This refuses a sandbox that hands out its answer key during a run, accepts a
malformed specimen, returns an empty report, or has no `key_claims`. It is the
same check continuous integration runs on every push.

## 7. Find the floor before you invite anyone

```bash
python -m whybox run my-sandbox --agent random --rounds 40
python -m whybox run my-sandbox --agent hillclimb --rounds 40
```

`random` is the floor. `hillclimb` optimizes with no understanding at all.
Both numbers have to exist before a result from a real investigator means
anything, because "the model scored 0.8" is not a finding until you know that
blind search scores 0.3.

If hill climbing reaches your ceiling easily, that is not a broken sandbox.
It is a sandbox where the score is the wrong measure and the notebook is the
whole result. Say so in your README, the way the example does.

## What makes a sandbox worth sharing

- **The right answer is knowable.** You can state the rule exactly. Without
  that there is nothing to grade insight against.
- **Score and understanding come apart.** If the only way to score well is to
  understand the rule, you have built a benchmark, which is fine but is not
  this.
- **The rule is outside what a model already knows.** A rule recoverable from
  memory tests recall. A rule that must be inferred from evidence tests
  something closer to science.
- **A smart investigator fails in a way you can explain.** The most useful
  sandboxes are the ones where failure is informative rather than random.
