# Decisions and open questions

## Decided by the project lead, 2026-10-13

**Primary audience: undergraduates learning how experiments work.** Zero setup
wins. A student should be able to play a sandbox by hand before any model does.
This is the decision with the widest effect on everything below.

What it already changed:

- `--agent human` was added, so a person can play a sandbox at the keyboard and
  be graded on their stated theory exactly as a model would be.
- It rules out, for now, anything that needs a download, a graphics card, an
  API key, or an account.

What it should change next:

- A quickstart that works in a browser or a notebook, since a terminal is a
  real barrier for a student who is not studying computing.
- A short teaching note: what to notice while playing, and why reaching the
  ceiling is not the same as understanding the rule.
- Instructions written for somebody who has never designed an experiment, not
  for somebody who already knows what a control is.

**Sealed wall: separate process plus an audit.** The oracle runs in its own
process and the sandbox folder carries an instruction not to look inside it.
Afterwards, the session log is checked. This is what the original paper's
authors did, and for a teaching audience it is the right trade, since the
alternative costs a student a container runtime before their first round.

The limit must stay written down where people will see it: this stops an
investigator from reading the rule out of its own memory, not from reading it
off the disk. Any published evaluation of a capable agent needs more.

**One repository to start.** Every sandbox is a folder under `sandboxes/`.
Splitting later means moving folders and adding an index, which is cheap. The
protocol and the manifest format were written so nothing above them knows the
difference.

**Second sandbox: another invented world, still laptop-sized.** No download,
no graphics card. It should exercise a different kind of reasoning from the
first, which is about grouping and silent positions. Candidates: a rule based
on where a character sits rather than which character it is, or one where the
score depends on a count rather than a pattern. Both are known from the paper
to be hard for current models in a way that is informative rather than random.

## Decided in the second round, 2026-10-13

**Feedback: show the answer key and let the student compare.** Already how it
works. The run now ends by pointing at `answer_key.json` and telling the
student to read it against their own notebook. No automatic report on what
they missed, and no instructor view, for now.

**Results: a public leaderboard.** The row format, the versioning rule, the
fingerprint, and the five things a published version still needs are in
[leaderboard.md](leaderboard.md). The local table works now:

    python -m whybox export runs/<folder> --append
    python -m whybox table

Rows sort by understanding before score. The thing to watch is that a public
leaderboard pulls toward optimizing whatever it displays, which is the exact
behavior this framework exists to expose.

**Credit: match the original authors' license and cite them formally.** Done.
The lead approved checking their repository on 2026-10-13. It carries the MIT
License, Copyright (c) 2025 Ananth Rao, so this project is MIT as well, with
an attribution section naming the paper and its eleven authors. The citation
is in `CITATION.cff`.

One condition came out of that check and is worth remembering: their README
states that the Malinois model weights are under the separate boda2 license.
Nothing here touches those weights today. A damp sandbox built on them would
inherit that condition, and MIT would not override it.

**Instructions: teach the habits explicitly.** The example sandbox now states
four habits up front: change one thing at a time, say in advance what would
prove you wrong, change the theory rather than the evidence, and treat a
negative result as a result.

The cost of this choice should stay visible. Those four habits are close to
the paper's own finding about where agents go wrong. A sandbox that hands them
over can teach them, but it can no longer measure whether the investigator
arrived with them. If the framework is ever pointed at models for evaluation
rather than at students for teaching, the instructions need a second version
with this section removed.

## Still open

**1. Who grades understanding when the rubric is not enough?**
The automatic grade is word matching and says so in its own output. The
model-review prompt is written but not wired up. The first time somebody
writes a notebook stuffed with the answer key's phrases, the automatic grade
stops being usable on its own.

**2. Does a repeated attempt have to be declared?**
Submitting the best of twenty runs is a different claim from submitting one
run, and the leaderboard row has no field for it yet.

**3. What is this called?**
`whybox` is a placeholder. A name that signals the teaching purpose would
serve the chosen audience better.

**4. How much hand-holding belongs in the instructions?**
There is a real tension. Telling a student to change one thing at a time makes
the exercise teachable. It also hands them the single most important finding
from the paper about where agents go wrong. A sandbox that teaches good
experimental habits and a sandbox that measures whether you have them are not
quite the same artifact, and the instructions text is where that gets settled.
