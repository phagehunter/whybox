# Publishing results

The project lead chose a public leaderboard. This is what that commits to, and
the parts that have to be settled before the first outside result arrives
rather than after.

## A row is two results, never one

```json
{"schema": 1, "sandbox": "codon-lite", "sandbox_version": "0.1.0",
 "oracle_kind": "dry", "agent": "hillclimb", "rounds_used": 40,
 "best_score": 5.0, "claims_found": 0, "claims_total": 4,
 "insight_graded_by": "rubric", "run_fingerprint": "af55a9f4dee9aeed",
 "submitted": "2026-10-13 14:24"}
```

`best_score` and `claims_found` sit beside each other and are never combined
into a single ranking number. Sorting is by insight first. Any future version
that adds an overall score undoes the reason the framework exists.

`insight_graded_by` says how the second number was produced: `rubric` for
automatic word matching, `model` for a reviewing model, `human` for a person.
These are not interchangeable, and a table that mixes them without saying so
is misleading.

## The versioning rule

**A sandbox version must change whenever the hidden rule, the contents of the
report, or the round budget change.** A score from before such a change is not
comparable to one from after, and nothing in the data will tell you that
unless the version does.

This is the rule most likely to be broken by accident, usually by an author
fixing a small bug in a hidden rule and leaving the version alone. Continuous
integration should refuse a sandbox whose rule changed without a version bump,
which requires storing a hash of the sealed folder alongside the version.
Not built.

## The fingerprint

Each row carries a short hash over the run's rounds, notebook, and summary. It
is not security. It means a row can be checked against the run it claims to
describe, and that a notebook edited after the fact produces a different
fingerprint rather than a quietly improved result.

## What a published leaderboard still needs

Nothing below exists yet. In rough order of necessity:

1. **A submission path.** A pull request adding a row, with continuous
   integration running the validator, is the cheapest version and needs no
   server.
2. **Run folders, not just rows.** A score with no notebook behind it cannot
   be checked. Submissions should include the run folder, or a link to it.
3. **A rule about self-reported grades.** The rubric is run by whoever submits.
   Either results are reproduced by a maintainer, or the table says plainly
   which rows were independently graded.
4. **A policy on repeated attempts.** Submitting the best of twenty runs is a
   different claim from submitting one run. The row has no field for this yet,
   and it should.
5. **Moderation.** Anyone can write a sandbox whose answer key makes any theory
   look correct. The validator cannot catch that; a person reading the answer
   key can.

## The tension to keep in view

A public leaderboard pulls toward optimizing the thing it displays. This
framework exists because optimizing the displayed number is exactly what a
capable agent will do instead of understanding the system. Putting insight in
the first sort position helps. It does not solve it, and the first time
somebody games the rubric by stuffing an answer key's phrases into a notebook,
the automatic grade stops being usable on its own.
