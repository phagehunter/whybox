# Security

## What this project does not protect

Read this before reporting anything, because the most likely report is already
answered here.

**The sealed oracle is not a security boundary.** It runs the hidden rule in
a separate operating-system process so that an investigator cannot read the
rule out of its own memory. It does not stop anything that can run commands on
the same machine from reading the sealed folder off the disk. This is a known
and documented limit, not a vulnerability.
[The architecture notes](docs/2026-10-13-architecture.md) explain what real
isolation would require.

**Grading can be gamed, and we publish the attack ourselves.** Run
`python -m whybox audit <sandbox>` to see how much of a sandbox's
understanding score a notebook containing only the right keywords collects.
For the example sandbox the answer is all of it. That is a property of word
matching, stated in the readme, not a defect to report.

## What is worth reporting

- A way to get the hidden rule back through a report, a score, or an error
  message during a run.
- A sandbox in this repository whose answer is reachable without the reveal
  step.
- Anything that executes attacker-controlled code when a user runs a command
  here, including through a crafted sandbox folder or a crafted run record.
- A leaderboard row that passes validation while misrepresenting its run.

## How to report

Use **GitHub's private vulnerability reporting** on this repository: the
Security tab, then "Report a vulnerability." It opens a private thread visible
only to the maintainer, so nothing in the first three categories above becomes
public before it is fixed.

If that is unavailable to you, open a public issue saying only that you have
something to report and asking for a private channel. Do not put the details
in it.

Expect an acknowledgement within a week. This is a small project with one
maintainer and no security team, and promising a faster response than that
would be dishonest.

## Supported versions

The most recent release only.
