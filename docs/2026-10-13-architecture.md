# Architecture

How the pieces fit, why each boundary is where it is, and what would have to
change to run this for real.

## The shape of a run

```
   INVESTIGATOR                 REFEREE                    SEALED
   (agent process)              (runner)                   (oracle process)

   proposes a specimen  ---->   logs it      ---->  JSON line over a pipe
   and says why                 starts the clock           |
                                                           v
                                                    validate the specimen
                                                    run the assay
                                                    build a small report
                                                           |
   reads the report     <----   logs it      <----  JSON line back
   writes a notebook            saves the notebook
   entry                        entry

   ... repeat for a fixed number of rounds ...

   states a final       ---->   writes run.json
   theory                       THEN asks the oracle for the answer key
                                and saves it beside the notebook
```

Three things in that picture do the real work.

**The number of rounds is fixed before the run starts.** Not "until it gets
bored" and not "until it stops improving". Two runs are only comparable if
they had the same budget, and an investigator that knows its budget will spend
it differently, which is itself worth watching.

**The report is small on purpose.** The oracle knows the per-specimen results,
which of its tests were hard, and exactly which rule produced the number. It
returns a handful of numbers. A sandbox that hands back everything it knows is
not testing much. Deciding what the report contains is the single biggest
design decision in a sandbox, and it belongs to the author, not the toolkit.

**The answer key comes out after the last round, never during.** The runner
starts a second oracle process with a `--reveal` flag only once the
investigator has committed to a final theory. There is no code path that lets
an in-progress run ask what the answer is.

## Why the oracle is a separate process

An AI agent with a shell can read any file it can reach and import any module
in its own process. If the oracle is an object in the same program, the hidden
rule is one `inspect.getsource` away, and the experiment measures nothing.

So the oracle speaks one line of JSON at a time through a pipe:

```
->  {"op":"measure","specimens":["ACGT..."]}
<-  {"ok":true,"result":{"scores":{"fitness":5.0}}}
```

That is a wall you can point at and explain to a reviewer, which matters more
than cleverness here.

It is **not** a security boundary. An investigator that can run shell commands
on the same machine can read `sealed/` off the disk. Running against a serious
agent needs one of:

- the oracle on a different machine behind an HTTP endpoint, with the agent
  holding only a URL and a token;
- the agent in a container with no network and no read access to the sandbox
  folder, talking to the oracle through a mounted socket;
- at minimum, an instruction not to look plus a check of the session log
  afterwards, which is what the original paper's authors did and reported.

The protocol in `protocol.py` was written to make the first option a change of
transport rather than a change of design. Nothing above it knows that the wall
is currently a pipe.

## Why score and insight never get averaged

A sandbox produces two results that measure different things:

- **score**: computed exactly, from the run record, no judgment involved.
- **insight**: did the investigator work out the rule? This needs reading.

The framework exists because these two come apart. An investigator can reach
the ceiling in five rounds by trying repeated characters and spend the other
thirty-five building a confident wrong theory. A single combined number would
hide exactly the thing worth seeing. So `judge.py` returns them as two separate
objects and offers no way to combine them.

Insight is graded in two passes, because the cheap pass is not trustworthy on
its own:

1. **Rubric.** The sandbox author writes `key_claims`: short statements a
   correct theory must contain, each with alternative wordings. Automatic,
   instant, and shallow. It can confirm a hit. It cannot understand a correct
   idea phrased in a way the author did not anticipate, and its own output
   says so.
2. **Model review.** A second model reads the notebook against the answer key
   and grades correctness, evidence, experiment design, and willingness to be
   wrong. The prompt is written in `judge.py`. The call is not wired up,
   because who judges, with what model, and whether a human signs off is a
   project decision rather than a technical one.

The rule that must survive any future version: the investigator being graded
is never the judge of its own run.

## What a sandbox author owns, and what they do not

| They own | The toolkit owns |
|---|---|
| what counts as a specimen | the round loop and the budget |
| what the assay measures | the sealed wall and the protocol |
| **what goes in the report** | the run record format |
| the hidden rule and the answer key | the score side of grading |
| the instructions text | the rubric machinery |
| the public facts in `describe()` | the command line |

The split is deliberate. Everything that requires knowing the science is the
author's. Everything that has to be identical across sandboxes for results to
be comparable is the toolkit's.

## The run record is the product

A finished run is a folder, and the folder is what gets shared:

```
runs/codon-lite__hillclimb__2026-10-13T1404/
  run.json          who ran what, final score, score trace, final theory
  rounds.jsonl      one line per round: submission, rationale, report, timing
  notebook.md       the investigator's own words, append only
  answer_key.json   the hidden rule, written only after the last round
  judge.json        the grade, written later
```

`rounds.jsonl` is the machine-readable trail and `notebook.md` is the
human-readable argument. Keeping them separate is what makes it possible to
ask "did the score go up?" and "did it understand why?" independently.

Append-only matters more than it looks. A notebook rewritten at the end reads
like a clean story that was never lived. The abandoned theory from round nine
is evidence, and it is often the most informative thing in the folder.

## Oracle temperature, and what each one costs

| | wet | damp | dry |
|---|---|---|---|
| source | a real experiment | a model trained on real data | an invented rule |
| a round takes | days to weeks | seconds to hours | milliseconds |
| ground truth | nobody knows it | the model's opinion | exact, by construction |
| can grade insight | only by argument | partly | yes, precisely |
| the catch | cost, noise, scheduling | inherits the model's biases | no biology in it |

A damp sandbox is the usual working choice, and the trap is that a model
trained on public data can be learned about from the public data rather than
from the sandbox. A dry sandbox is the only one that can prove an
investigator inferred a rule rather than recalled it, which is why the
worked example here is dry.

## Distribution: sandboxes as separate repositories

A sandbox needs its own repository, not a folder in this one.

- Its hidden rule has a different access story than the toolkit. Some sandboxes
  should keep `sealed/` in a private repository entirely.
- Its data may be large, licensed, or restricted.
- Its author is a domain scientist who should not need to send a pull request
  to a toolkit maintainer to publish a sandbox.

So: a sandbox is any folder containing a valid `sandbox.yaml`, found by path or
by an install step. A central index is a list of repository URLs, and
`whybox check` is the entry requirement. Continuous integration runs the
same check on every push, and refuses a sandbox whose answer key is reachable
during a run.

Versioning follows from the same place. A sandbox's version number must change
whenever the hidden rule, the report contents, or the round budget change,
because a score from before the change is not comparable to one from after.
The version is recorded in every run.

## Open design questions

These are decisions, not bugs. They are listed in
[2026-10-13-open-questions.md](2026-10-13-open-questions.md), and the answers
determine what gets built next.
