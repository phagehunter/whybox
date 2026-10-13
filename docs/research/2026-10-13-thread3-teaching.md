# Thread 3: the game, the evidence, and getting it to students

Two questions. What does the research on hidden-rule games say we should
change, and how does a student play this without installing anything.

## The finding that forces a design decision

**The sealed oracle cannot be a separate process in a browser.** Python in the
browser runs through Pyodide, and its own migration guide states it plainly:

> subprocess, os.system, os.popen, and related calls don't work in WebAssembly

[Source](https://pyodide-build.readthedocs.io/en/latest/how-to/migrate.html).
Worse for us, the
[constraints page](https://pyodide.org/en/stable/usage/wasm-constraints.html)
lists threading, multiprocessing, and sockets as importable but non-working,
so `import subprocess` succeeds and only the spawn fails. Any browser version
must detect the platform rather than catch an import error.

And in a browser nothing is truly hidden, because the page runs on the
student's own machine and everything it loads is readable in developer tools.

**What to do instead: a commitment.** Keep the oracle in the same process, but
at the start of a session print a hash of the hidden rule. The student copies
it into their notebook. At the end, the revealed rule must hash to the same
value. This does not stop a determined student from looking, and it is not
meant to. It preserves the two properties that actually matter for teaching:
the oracle cannot change the rule once play has started, and a student cannot
claim afterwards that they had it all along. Honesty about which property is
being protected is the point.

## How to reach students, ranked

1. **A browser notebook site on GitHub Pages.** Zero install, zero login, no
   account, works on a school Chromebook, and it matches what this account
   already publishes, which is static sites.
   [Deploy guide](https://jupyterlite.readthedocs.io/en/stable/quickstart/deploy.html).
   Shipping our own package into it is a solved problem.
   [How](https://jupyterlite-pyodide-lock.readthedocs.io/en/stable/). The cost
   is the oracle change above, and the site cannot collect anything.
2. **Colab, as a parallel path.** One notebook plus a badge, about ten minutes
   of work. It is real Python, so the existing process-separated oracle works
   unchanged. It needs a Google account, which is a real barrier at some
   institutions, and the student can read the oracle source directly.
3. **Marimo exported to the browser**, if a polished app is wanted rather than
   a notebook. [Guide](https://docs.marimo.io/guides/wasm/). Same browser
   limits apply.
4. **Codespaces**, as the instructor and contributor environment, not the
   student path. Note that GitHub Classroom is being retired, so do not build
   a course workflow on it.
5. **Binder: offer a badge, promise nothing.** The project still describes
   itself as a pilot with no uptime guarantee
   ([status](https://mybinder.readthedocs.io/en/latest/about/status.html)) and
   its session volume fell sharply across 2025
   ([report](https://2i2c.org/blog/binder-report/)).

## What the research on these games says

This puzzle is old and well studied, and four findings bear directly on our
instructions.

**1. Name the complement, and say it out loud.** The single largest known
effect in this literature. Reframing the classic number-sequence task so that
the player hunts for two labeled, complementary categories rather than one
rule raised solution rates from roughly a fifth of participants to over half.
Later work showed the gain comes specifically from players generating an
instance of the contrasting category.
[Mechanism](https://eprints.lancs.ac.uk/id/eprint/3551/). For us: report a
category label alongside the number, and ask the notebook for both the rule
for high scores and the rule for low ones.

**2. Positive testing is not a bias, it is a reasonable strategy that fails in
one specific setup.** Klayman and Ha showed it only misfires when the true
rule is strictly broader than the learner's guess, which is exactly how the
classic task was built. Teaching students that they are simply biased is
therefore the wrong lesson. Ship some worlds where the true rule is narrower
than the obvious guess, so students learn when the strategy works and when it
does not.

**3. Predicting well is not understanding, and this has been measured.** A
Zendo-style benchmark found that high accuracy at labeling observed examples
does not imply recovery of the underlying rule
([paper](https://arxiv.org/abs/2607.08233)), and an Eleusis benchmark found
every model tested was overconfident
([repo](https://github.com/scienceetonnante/eleusis-llm-benchmark)). This is
our thesis, independently confirmed, and we should cite it. For teaching: make
the student commit a written hypothesis and a confidence number partway
through, then show them afterwards how the two came apart.

**4. Charge for guesses.** The Eleusis benchmark scores as turns remaining
minus a penalty for each wrong guess. Without a cost, players spray guesses
instead of designing experiments. Adopt the shape and print the running cost
each turn.

**5. Order the worlds by measured difficulty, not by vibes.** That same
benchmark computes complexity metrics over its rules, but only after the fact.
We can do it before.

## The nearest neighbors

| Project | Verdict |
|---|---|
| [Eleusis LLM benchmark](https://github.com/scienceetonnante/eleusis-llm-benchmark) | The closest sibling. MIT, Python, worth reading before writing another line. |
| [ZendoWorld](https://arxiv.org/abs/2607.08233) | Visual rule induction; separates perceiving, inferring, and experimenting. |
| [Active Zendo with language models](https://arxiv.org/abs/2402.06025) | Fuzzy rules and online inference needed to match human behavior. |
| [RULEARN](https://arxiv.org/abs/2408.10455) | Agents form plausible hypotheses and fail to refine them through interaction. |
| [AbstractPlay/zendo](https://github.com/AbstractPlay/zendo) | Needs a human moderator, so there is no oracle to borrow. |
| [Romesburg 1979](https://digitalcommons.usu.edu/envs_facpub/20) | The citable classic for using this game to simulate inquiry. |
| [Eleusis with biology trainees](https://hal-lirmm.ccsd.cnrs.fr/lirmm-00193672/document) | The best quasi-experimental classroom evidence found. |

## Caveats the thread itself raised

No controlled classroom trial of Zendo was found; the evidence is practitioner
reports plus the older Eleusis literature. Two GitHub facts, a student compute
allowance and a retirement date, came from search summaries rather than a
direct read, and should be confirmed before anyone relies on them.
