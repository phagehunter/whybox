# Thread 1: how agent evaluation harnesses are built

What the established runners do about the three problems we also have: letting
outsiders add a task, keeping the answer away from the thing being tested, and
versioning so old scores stay meaningful.

## The landscape, and a warning in it

| Project | Status as of October 2026 |
|---|---|
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | Active, about 3,000 stars, MIT. The current center of gravity. |
| [Inspect Evals](https://github.com/UKGovernmentBEIS/inspect_evals) | Active, about 700 stars. The task collection. |
| [METR task standard](https://github.com/METR/task-standard) | **Archived.** Its readme points people to Inspect. |
| [METR Vivaria](https://github.com/METR/vivaria) | **Archived.** |
| [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | Active, about 14,000 stars. |
| [HELM](https://github.com/stanford-crfm/helm) | **Maintenance mode** since June 2026. |
| [OpenAI Evals](https://github.com/openai/evals) | Stalled. No longer accepts tasks that carry custom code. |
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) | Active. |
| [MLE-bench](https://github.com/openai/mle-bench) | Leaderboard closed to new submissions, April 2026. |
| [DiscoveryWorld](https://github.com/allenai/discoveryworld) | Apache 2.0, about 226 stars. The closest thing to us. |
| [BixBench](https://github.com/Future-House/BixBench), [LAB-Bench](https://github.com/Future-House/LAB-Bench), [DiscoveryBench](https://github.com/allenai/discoverybench) | Science-specific, all quiet since 2025. |

The warning is the archive column. Two serious attempts at a general task
standard are now archived and redirect to Inspect. A third is in maintenance
mode and a fourth stopped accepting contributions. **Writing a new standard is
the thing that keeps failing in this field.** The sensible posture is to be a
small, opinionated teaching tool that can also hand its sandboxes to Inspect,
not a rival runner.

## The one genuinely good piece of news

The hidden-rule niche is essentially unoccupied. The nearest work is
[ZendoWorld](https://github.com/ml-research/ZendoWorld) at one star,
[FalsifyBench](https://github.com/leobertolazzi/FalsifyBench) at zero, and the
[WILT paper](https://arxiv.org/abs/2410.10998). There is no incumbent to
displace, which is unusual and worth saying out loud in the readme.

## How outsiders add a task

The field converged, then moved again, and the second move is the one that
matters to us.

**First convergence: a manifest plus a code file.** lm-evaluation-harness uses
`lm_eval/tasks/<dataset>/<task>.yaml` with a `metadata.version` integer.
Inspect Evals uses a four-file folder containing a readme, an init file, an
`eval.yaml`, and the task code. The manifest is schema validated and
**unknown keys fail validation**, which is stricter than our loose reader.

**Second move: stop accepting code at all.** Inspect Evals now keeps
third-party evals out of the repository. An author keeps their code in their
own repository and registers it with a pinned 40-character commit hash, their
own maintainer list, and uploaded run logs from two different models. OpenAI
Evals made the same decision and stalled anyway. The reason is maintenance
cost: every accepted code contribution is a thing the maintainer must keep
working forever.

For us, this is a design instruction rather than a nicety. We decided to start
with one repository holding all sandboxes. That is fine at one sandbox and
becomes the thing that kills the project at twenty. The cheap insurance is to
make a sandbox discoverable through a declared entry point rather than by
scanning a folder, so that an outside sandbox is possible later without
redesigning anything.

**Discovery mechanism.** Inspect finds packaged tasks through a
`pyproject.toml` entry point, not by walking directories. We currently walk
directories. Both can coexist.

## Keeping the answer away from the agent

This is where the comparison is least flattering to us.

**Inspect** gives each sample its own container and sets the generated compose
file to `network_mode: none`. A hand-written compose file does **not** inherit
that, which is a documented trap. Inspect's docs say nothing about hiding a
target from the model, because its tasks mostly do not need to.

**METR**, now archived, is the only project that treated answer-hiding as a
first-class problem. The agent ran as an unprivileged user; the answer lived
in root-owned files and an auxiliary virtual machine the agent could not reach.
A task could run a service on localhost that the agent could query but not
inspect. That is exactly our oracle, done properly.

**MLE-bench** ships a rule-violation detector and a plagiarism detector, and
publicly documents which of its competitions have known data leaks.

**LAB-Bench** withholds about a fifth of its data as a private test set and
embeds a canary string so that anyone can later detect whether the benchmark
leaked into training data.

Three consequences for us, in order of how much they matter.

1. **Our `answer_key.json` is a leak surface, and the leak is real, not
   theoretical.** We write the key into the run folder after the final theory
   is recorded, which is correct for a student. But run folders accumulate
   under `runs/`. An agent with a shell, on its second run of the same
   sandbox, can read the answer out of the first run's folder. Nothing stops
   it today.
2. **"Sealed" promises more than a subprocess delivers.** Our architecture
   doc says so; the readme does not, and the readme is what people read.
3. **There is no canary and no cheat detector.** Both are cheap. A canary
   string in the sealed folder costs one line and makes later contamination
   detectable. A scan of a run's own records for reads of `sealed/` is a
   plausible afternoon.

## Versioning

Inspect Evals' scheme is the best available and is worth copying almost
exactly. A two-part version like `1-A` on each task. The **number** goes up
when results may no longer be comparable, which includes scoring changes,
data changes, prompt changes, and bug fixes that move the numbers. The
**letter** goes up when the interface changes, such as a renamed parameter.
Neither part ever resets. Every bump requires a changelog line.

Our rule, "change the version when the hidden rule, the report, or the round
budget changes," is the same idea stated less precisely. The two-part form is
better because it distinguishes "your old score is now meaningless" from "your
old command line no longer runs," which are different emergencies.

lm-evaluation-harness does the simpler thing: an integer and a dated changelog
entry citing the pull request.

## The precedent we should be citing

**DiscoveryWorld already separates the two numbers we separate.** It reports a
procedural task score alongside answers to "critical questions" that test
whether the agent actually understood the discovery. Our score-versus-insight
split is not an invention, and saying so makes it more credible rather than
less. We should cite it.

## What this thread says to change

1. Say plainly in the readme that the wall is a process boundary, not a
   security boundary.
2. Stop writing the answer key where a later run can read it, or at minimum
   make that mode available and document the risk.
3. Add a canary string to the sealed folder.
4. Move to a two-part sandbox version and record it in every run.
5. Make sandbox discovery work through a declared entry point as well as a
   folder scan, so outside sandboxes become possible without a redesign.
6. Validate the manifest against a schema and reject unknown keys.
7. Report results over at least three seeds with a spread, not a single run.
8. Cite DiscoveryWorld for the two-number design.
9. Do not attempt a general standard. Offer an Inspect adapter eventually.

## Traps, each with the project that fell into it

- **A new standard nobody adopts.** METR's task standard and Vivaria, both
  archived.
- **Accepting code contributions you must then maintain.** OpenAI Evals,
  stalled.
- **Shipping a sandbox with the answer visible in its own data.** MLE-bench
  had to publish a list of affected competitions.
- **Caching a result on a run identifier alone**, which silently returns a
  stale score. SWE-bench documents this as a footgun.
- **Letting the readme rot into a status notice.** HELM's readme now mostly
  explains that the project is in maintenance mode.
