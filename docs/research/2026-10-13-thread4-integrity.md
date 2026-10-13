# Thread 4: how leaderboards fail

We promised a public leaderboard. This is what happens to them, and which
failures our design invites specifically.

## How results actually get accepted

| Model | Who computes the score | Examples |
|---|---|---|
| Self-reported row in a file | The submitter | Early open model leaderboards, Papers With Code |
| Self-reported, artifacts required, maintainer re-grades from recorded output | Submitter runs, maintainer checks | [SWE-bench experiments](https://github.com/SWE-bench/experiments/blob/main/README.md) |
| Submission round with cross-review and sampled audit | Submitter, then peers | [MLPerf](https://github.com/mlcommons/policies/blob/master/submission_rules.adoc) |
| Hosted execution against a hidden set | The maintainer's server | Kaggle, [ARC Prize](https://arcprize.org/policy) |
| Independent re-run of every entry | A third party | [HAL](https://hal.cs.princeton.edu/about) |

**Start at the second tier.** A bare row of numbers is an unfalsifiable
assertion. Requiring the run folder alongside it means anyone can re-grade
from recorded output without re-executing anything, which is the only tier a
project with no server can honestly operate. The SWE-bench rule is the model:
submit the predictions, the per-instance outputs, and one reasoning trace.

## The five risks our design invites

**1. A best-of-many score with the many hidden.** Our row reports
`best_score` and says nothing about how many runs produced it. The precedent
is large: a team was barred from a vision challenge's test server for a year
over repeated submissions from many accounts, and
[The Leaderboard Illusion](https://arxiv.org/abs/2504.20879) shows private
best-of-N testing biases a major chat ranking. MLPerf's answer is a fixed
minimum run count, dropping the fastest and slowest, and reporting the mean of
the rest. **Fix:** record every run, the number of runs, and the rule used to
pick, and make a trimmed mean the primary number.

**2. The hidden rule leaks, into a context window or into training data.**
Agents have been caught searching the web for benchmark answer keys, and a
replication study found double-digit score drops when a popular benchmark was
rebuilt from scratch ([GSM1k](https://arxiv.org/abs/2405.00332)). **Fix:** a
canary string in every sealed file, so that contamination becomes detectable
later, plus a held-out world that never ships publicly.

**3. The fingerprint is computed by the party being graded.** A hash over
files the submitter produced proves internal consistency and nothing else.
**Fix:** also hash the sandbox definition and the grader, publish the expected
value per release, and reject a row whose sandbox hash does not match.

**4. The understanding number is the easiest number in the system to
inflate.** Word matching rewards a notebook stuffed with the answer key's
vocabulary. This is the same shape as verbosity bias, which one evaluation had
to [regress out](https://arxiv.org/abs/2404.04475), and the same shape as the
agent benchmark where
[a null agent that returned nothing scored as a success](https://arxiv.org/abs/2507.02825).
**Fix:** ship the attack as a baseline. A null investigator that submits
nothing and writes a notebook containing every keyword, published on the board
as the floor. If a real entry cannot beat the stuffing baseline, its number
means nothing. Also require a quoted piece of evidence per claim.

**5. Silent version drift.** The standard answer is a version that must be
bumped on any change that moves numbers, plus a dated changelog entry. **Fix:**
store the sandbox version, the sandbox hash, and the grader version in every
row, and never interleave rows from different versions in one table.

## The verdict on our sorting rule

Our plan was to sort by understanding and never combine the two numbers.
Directionally right, and it does resist the usual failure of a blended score.
But it has a specific flaw worth stating:

**Sorting by understanding makes the least verifiable number the one worth
gaming.** We took the softest measurement in the system and made it the rank.
Three concrete consequences:

- **A degenerate winner is possible.** An investigator that runs no experiment
  and writes a confident notebook can top the board at a score of zero.
  There must be a minimum score before an understanding rank is granted.
- **Ties will dominate.** Four claims over a small denominator produces mass
  ties, and the undefined secondary sort silently becomes the real ranking.
  Publish the tie-break.
- **A model-graded number is not reproducible** across grader versions, so two
  rows may have been measured with different instruments.

The honest fix is not to abandon the design but to add a gate: a score floor
to be listed at all, a published tie-break, the stuffing baseline as the
floor, and the grader version in every row.

## Fields the row is missing

Schema version, status (unverified, reproduced, flagged), submitter and
contact, a link to the full run artifacts, the list of runs with seeds and a
selection rule, a trimmed mean, the sandbox hash, the toolkit version, the
grader version and rubric hash, the exact dated model identifier and sampling
settings where a model played, token and time cost, whether a human was in the
loop, a contamination declaration, and a license.

Two reporting checklists are free and need no infrastructure:
[BetterBench](https://arxiv.org/abs/2411.12990) and the
[agentic benchmark checklist](https://arxiv.org/abs/2507.02825). Use them as a
self-audit.

## On model graders, for when we wire one up

Agreement with human judges above eighty percent is reported for a strong
model on a chat benchmark, but with documented biases: position, verbosity,
and preferring its own output
([judging study](https://arxiv.org/abs/2306.05685),
[self-preference](https://arxiv.org/abs/2404.13076)). The rule already in our
grader, that the investigator never judges its own run, is the right one and
is independently supported.

## A governance note

One benchmark drew sustained criticism over undisclosed funding from a lab
whose models it evaluated, combined with a submitter-owned hold-out set. The
cheap insurance is a submitter field and a conflict-of-interest field from day
one, before there is anything to disclose.
