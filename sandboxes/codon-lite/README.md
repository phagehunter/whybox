# codon-lite

A worked example of a complete science sandbox. Small enough to read in one
sitting, fast enough to run on a laptop with no GPU and no downloads.

## What is hidden

A sequence is read in non-overlapping groups. Each group becomes one of two
kinds of bead. The chain of beads is folded on a square grid, and the score
counts how many sticky beads end up touching sticky beads. The grouping and
the bead rule live in `sealed/` and the investigator never sees them.

## Why it is built this way

The score ceiling is easy to reach and the rule is hard to state. That gap is
the entire point. An investigator can hit the maximum within a few rounds by
trying repeated characters, which means the score alone cannot tell you
whether anything was understood. Only the notebook can.

## Two worlds, one change

Set `world:` in `sandbox.yaml`:

- `single-position` - the first character of each group is ignored. Half of
  all single-character changes do nothing, and the investigator has to decide
  whether that means a silent position or a noisy machine.
- `paired` - neither character means anything alone; only the combination
  does. Any theory built on per-character effects will keep breaking.

The folding physics is identical in both. Only the genetics differ, so a
difference in results is a difference in the rule, not the chemistry.

## Run it

    python -m whybox run codon-lite --agent human --rounds 15
    python -m whybox run codon-lite --agent hillclimb --rounds 40
    python -m whybox judge runs/<the folder it printed>

`hillclimb` optimizes without understanding. Over 40 rounds it reaches 5 of a
possible 6 and states none of the four true claims about the rule. Random
guessing reaches 6. That contrast is what a real investigator has to beat, and
it is the second column that has to move, not the first.

## How honest is the grading here

    python -m whybox audit codon-lite

**4 of 4.** A notebook containing this sandbox's answer-key vocabulary and no
experiments at all collects the full understanding score. The word-matching
grade on this sandbox is therefore not evidence on its own, and that number is
published here rather than left for someone else to discover.

## Versions

Two parts: the number rises when old scores stop being comparable, the letter
when only the interface changes. See [the policy](../../docs/versioning.md).

| Version | What changed |
|---|---|
| `1-B` | The toolkit was renamed, so the command changed. Letter bump, not number: the hidden rule, the report, and the round budget are untouched, so a score from `1-A` sits in the same table as one from `1-B`. |
| `1-A` | First version under the two-part scheme. Canary markers added to the answer key, and a commitment hash published at round zero. The hidden rule, the report, and the round budget are unchanged from the earlier `0.1.0`, so scores carry over. |
