# whybox

**Status: scaffolding.** This is a working skeleton with one complete example,
built to show what the full system would look like. It is not the full system.
See [What is deliberately missing](#what-is-deliberately-missing).

A science sandbox is a closed room with a locked machine in it. You can put
something into the machine and read a number off the display. You cannot open
the machine. Your job is to work out what is inside.

That is a stripped-down version of experimental science, and it turns out to
be a good way to test whether an AI agent can actually do science, as opposed
to being good at getting a high score. Those two things look identical from the
outside, and a sandbox is built to tell them apart.

This repository is the plumbing: a way to write one of these rooms, run an
investigator inside it, and grade what came out.

## The idea in one example

Run the example sandbox with a baseline investigator that optimizes without
thinking. It keeps whatever scored best and changes one character at random:

```bash
python -m whybox run codon-lite --agent hillclimb --rounds 40
python -m whybox judge runs/<the folder it just printed>
```

It reaches 5 out of a possible 6. By the usual standard of a benchmark, that
is a good result. Then look at the grade:

```
"score":   { "best_score": 5.0, "rounds_used": 40 }
"insight": { "claims_total": 4, "claims_found": 0 }
```

Four things were true about the hidden rule, and the investigator stated none
of them. It never worked out that the sequence is read in groups, that half the
positions do nothing, or what the number was counting. It scored well and
learned nothing, and the run record says so in two separate numbers that are
never averaged together.

Every sandbox in this framework is built to make that gap visible.

## Two things to know before you trust a number from this

Both are stated here rather than buried, because both limit what the numbers
mean.

**The sealed wall is a process boundary, not a security boundary.** The hidden
rule runs in a separate operating-system process, so an investigator cannot
read it out of its own memory. Anything that can run commands on the same
machine can still read the sealed folder off the disk. Running this against a
capable agent needs real isolation, which is not built.

**The understanding score is word matching, and it can be fully inflated.**
We ship the attack rather than waiting for someone to find it:

```bash
python -m whybox audit codon-lite
```

It writes a notebook containing the answer key's vocabulary and nothing else,
runs no experiments, and reports what that scores. For the example sandbox it
scores four out of four. Treat the understanding column as evidence only when
a person or a second model has read the notebook.

## The three pieces

Every sandbox has the same three parts, whatever science it is about.

| Piece | What it is | In the example |
|---|---|---|
| **specimens** | the things you can submit | a 24-character sequence |
| **assay** | the measurement performed on them | fold it, count the sticky contacts |
| **oracle** | the sealed machine that runs the assay | `sandboxes/codon-lite/oracle.py` |

Oracles come in three temperatures, and the choice is the most consequential
one a sandbox author makes:

- **wet** - a real physical experiment. Real, slow, expensive, noisy. Nobody
  can tell you the right answer, because nobody knows it.
- **damp** - a computer model trained on real measurements. Fast enough to run
  thousands of times, and wrong in whatever ways the model is wrong.
- **dry** - a rule somebody invented. No biology in it at all, so nothing found
  is a discovery about nature. In exchange you know the exact right answer,
  which means claims can be graded instead of argued about.

The example sandbox is dry, because a dry sandbox is the only kind that can
demonstrate the framework honestly on a laptop in ten seconds.

## Layout

```
whybox/              the toolkit. Knows no science.
  spec.py                reads sandbox.yaml
  oracle.py              the base class a sandbox author fills in
  protocol.py            the JSON line format spoken through the wall
  sealed_server.py       runs an oracle in its own process
  runner.py              the round loop and the referee
  record.py              what a run leaves on disk
  judge.py               grades score and insight separately
  agents/                investigators: human, random, hillclimb, model stub
  leaderboard.py         turns a finished run into one comparable row
sandboxes/
  codon-lite/            a complete worked example
    sandbox.yaml         the contract, readable without opening any code
    instructions.md      what the investigator is told
    oracle.py            the measurement
    sealed/              the hidden rule. Never leaves this folder.
examples/example-run/    a finished run, so you can read the output first
leaderboard/             collected rows, with the two baselines already in
docs/                    architecture, and how to add your own sandbox
```

## Play it in a browser, right now

**<https://curtishoffmann.com/whybox>** runs one sandbox with no install, no
account, and no Python. Submit a sequence, read one number, and work out what
produces it.

That page reimplements the example world in JavaScript, because a browser
cannot run the oracle in a separate process. The two implementations are held
together by a test that runs both and compares their answers, so they cannot
drift apart silently. In a browser the rule is readable in developer tools by
anyone who looks; what the page protects instead is that the rule cannot
change while you play, which the fingerprint shown before your first
experiment makes checkable.

## Play it yourself first

Before pointing any model at a sandbox, spend ten minutes being the
investigator. It is the fastest way to understand what is being measured:

```bash
python -m whybox run codon-lite --agent human --rounds 15
```

You submit a sequence, you get one number, and you say what you think the rule
is. At the end you are graded on your stated theory, exactly as a model would
be. Most people reach the top score long before they can explain it, which is
the whole point, felt rather than read.

## Running it

Python 3.9 or newer. No dependencies for anything above; the optional model
investigator needs the `anthropic` package and an API key.

```bash
python -m whybox list                      # what is installed
python -m whybox check codon-lite          # validate before sharing
python -m whybox run codon-lite --agent hillclimb
python -m whybox judge runs/<folder>
python -m whybox audit codon-lite          # attack our own grader
python -m whybox export runs/<folder> --append   # add a result row
python -m whybox table                     # see the rows so far
python -m unittest discover -s tests           # 31 tests, about five seconds
```

A run by a person ends by writing the hidden rule into the run folder, so the
student can read it against their own notebook. A run by anything else does
not, because run folders pile up and the next run would be able to read the
last one's answer. Every run records a hash of the rule either way, which
proves the rule did not change partway through.

## Writing your own

See [docs/adding-a-sandbox.md](docs/adding-a-sandbox.md). The short version:
copy `sandboxes/codon-lite/`, write three methods on the oracle class, put
anything secret in `sealed/`, and run `whybox check` until it passes.

A sandbox is a research contribution in its own right. The interesting ones
are the ones where a smart investigator fails in a way you can explain.

## What is deliberately missing

Honest list of what this scaffolding does **not** do yet:

- **No real model agent.** `agents/claude_agent.py` shows the shape and makes
  the API calls, but has no retries, no cost tracking, no resuming, and no
  tool use beyond submitting a specimen.
- **No model-based grading.** `judge.py` builds the prompt a reviewing model
  would read and stops there. The automatic grading is word matching, which
  misses a correct idea phrased differently, and it says so in its own output.
- **No damp or wet example.** Both are described in the architecture doc and
  neither is built. A damp sandbox needs a trained model and a GPU; a wet one
  needs a lab and a way to wait days for a round.
- **No published leaderboard.** The row format, the versioning rule, and a
  local table exist. There is no server, no submission path, and no
  moderation. See [docs/leaderboard.md](docs/leaderboard.md).
- **The sealed wall is a process boundary, not a sandbox in the security
  sense.** It stops an investigator from reading the answer out of memory. It
  does not stop one that can run arbitrary shell commands on the same machine
  from reading `sealed/` off the disk. See the architecture doc for what real
  isolation would require.

## How to cite this

Cite the paper, not this repository, if you are citing the idea. The framework
is theirs. `CITATION.cff` has the full entry, and GitHub turns it into a
"Cite this repository" button.

## Where the design decisions come from

Before publishing, four independent searches looked at how comparable projects
handle task packaging, isolation, versioning, teaching delivery, and
leaderboard integrity. The method, the full source register, the findings, and
the list of what was adopted and what was rejected and why are in
[docs/research](docs/research/2026-10-13-methodology.md).

Three things in this repository exist because that review said so: the answer
key no longer sits where a later run can read it, the grader audit above, and
the two-part sandbox version explained in [docs/versioning.md](docs/versioning.md).

## Credit

The framework, the three-part structure, the wet/damp/dry distinction, and the
example of an invented genetic world all come from the science sandboxes paper
by Rao and colleagues at the Broad Institute, the Jackson Laboratory, and Yale
(arXiv 2608.30165). Their own code is at
<https://github.com/asr2210/science-sandbox>. This repository is an independent
scaffold for making that framework easy for other people to build on, and it
reimplements the ideas rather than their code. This project is **not authored
or endorsed by them**, and it is not an official or reference implementation
of their framework. The formal citation is in `CITATION.cff`.

Licensed MIT, matching their repository, which is MIT, Copyright (c) 2025
Ananth Rao. No code was copied from it. See `LICENSE`.
