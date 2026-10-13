# Contributing

The most useful contribution is a new sandbox, not a change to the toolkit.

## Getting it running

No dependencies. Python 3.9 or newer.

```bash
git clone <this repository>
cd <this repository>
python3 -m unittest discover -s tests
```

If the tests pass, you are set up. There is nothing else to install.

## The most useful thing you can do

**Write a sandbox.** [The guide](docs/adding-a-sandbox.md) walks through it.
You need a system where you know the rule and an investigator does not; the
code around that is about forty lines.

A sandbox is a contribution in its own right, and the interesting ones are the
ones where a capable investigator fails in a way you can explain.

Before you propose one, run:

```bash
python -m whybox check <your sandbox>
python -m whybox audit <your sandbox>
```

The first refuses a sandbox that hands out its answer during a run, accepts a
malformed specimen, or has no claims for the grader to check. The second
attacks your own grading rules and tells you how much of your understanding
score a notebook full of keywords can collect without running any experiment.
Both numbers belong in your sandbox's readme, including when they are
unflattering.

## Changing the toolkit

Smaller changes are easier to accept than larger ones. Before a large one,
open an issue describing the problem rather than the solution.

Two rules are not up for negotiation, because the project has no point without
them:

1. **Score and understanding are never combined into one number.** Not in the
   grader, not in the leaderboard, not in a convenience helper.
2. **The investigator never grades its own run**, and nothing sends the hidden
   rule back through a report.

A change that quietly relaxes either will be declined even if it is otherwise
good.

## Style

- Comments explain why, not what. If a line needs a comment to say what it
  does, rename something instead.
- Plain words over jargon. A second-year undergraduate is the reader.
- American English.
- Tests go with the change. A fix with no test that would have caught it is
  half a fix.

## Reporting a problem

Use the question template if you are unsure whether something is a bug. It
usually is not, and asking costs nothing. Students especially: a question is a
welcome issue, not a nuisance.

## What happens to your contribution

This is a small project with one maintainer, so a response may take a week.
If a change is declined, the reason will be in the thread rather than left
implicit.
