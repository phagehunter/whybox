# Validation edits

Every finding, run through the three tests in the
[methodology](2026-10-13-methodology.md): does it recur across independent
threads or come from an authority, is it proportionate at this size, and does
it survive an undergraduate audience.

Rejected items are listed too, with reasons, because a rejected idea with a
recorded reason is cheaper to revisit than one nobody wrote down.

## Settled: the name

The working name, `sandboxkit`, was taken on the Python package index by a
tool for sandboxing untrusted code with operating-system isolation. The
collision was bad because of what it collided with: both projects are Python,
both say "sandbox," and the two meanings sit one search result apart.

Twenty-five candidates were checked for availability. The project lead chose
**whybox**, on 2026-10-13. It states the thesis rather than the mechanism: the
score is the what, and this project exists for the why. The package name, the
command, the module, and the canary marker all changed with it.

## Adopted, and implemented now

### Integrity, which is where the research was least flattering

**1. The answer key no longer sits where the next run can read it.**
Previously the key was written into every run folder after the final theory.
That is right for a student and wrong for an agent, because run folders
accumulate and an agent with a shell can read the key out of an earlier run.
Now the key is written only when the investigator is a person, and every run
records the key's hash instead. Threads 1 and 4 both flagged this; thread 1
called it a leak surface, thread 4 found agents caught hunting for answer keys
in the wild.

**2. A commitment hash is printed before the first round.** The hash of the
sealed rule is shown at the start and recorded in the run. It proves the rule
did not change mid-game and that nobody can claim afterwards they had it all
along. It does not stop anyone from looking, and the documentation says so.
This comes from thread 3, where it is the only honest option left once the
oracle has to run in the same process as the student in a browser.

**3. A canary string in every sealed file.** Found independently by threads 1
and 4. It costs one line and makes it possible, years from now, to detect that
this sandbox's answers leaked into a training set.

**4. An audit command that attacks our own grader.** The understanding score
is produced by word matching, which means a notebook stuffed with the answer
key's vocabulary scores full marks having run no experiments at all.
`whybox audit` builds exactly that notebook and reports what it scores.
The number it prints is the floor below which the understanding column means
nothing. Thread 4's precedent is the agent benchmark where a null agent that
returned nothing was scored as a success.

**5. A two-part sandbox version.** The number goes up when old scores stop
being comparable. The letter goes up when the interface changes. This is the
current convention in the most active harness, and it distinguishes "your old
score is meaningless" from "your old command no longer runs," which are
different emergencies. Threads 1 and 4 agreed.

**6. The leaderboard row carries what a reader needs to disbelieve it.**
Added: status, submitter, a link to the full run, the number of runs and how
the reported one was selected, the sandbox hash, the toolkit version, the
grader version, whether a person was in the loop, and a contamination
declaration.

**7. A score floor and a published tie-break.** Thread 4's sharpest point:
sorting by understanding makes the least verifiable number the rank, and an
investigator that runs no experiment and writes a confident notebook could
top the board at a score of zero. A row now needs a minimum score before it is
ranked by understanding at all, and the tie-break is written down instead of
being whatever the sort happened to do.

### Repository credibility

**8. The community files reviewers check for**: contributing guide, code of
conduct, security policy, changelog, and issue templates. One template is a
question rather than a bug, because students do not file bugs and a form that
only offers "bug report" silences them.

**9. The readme says plainly that the wall is not a security boundary.** It
was in the architecture document, which nobody reads first.

**10. Attribution wording tightened.** Both review bodies check that related
work is cited properly. The readme and citation file now avoid "official,"
"reference implementation," and "companion to," and state that this is an
independent implementation, not endorsed by the original authors.

**11. Dependency updates scoped to workflow actions only**, since there are no
Python dependencies to update.

## Adopted, documented, not yet built

These passed the tests but are features rather than fixes, and the brief was
to validate rather than to expand.

- **Repeat every result over at least three seeds** and report a trimmed mean,
  the way the large machine-learning benchmarks do. The row already records
  the run count so that a single run is visibly a single run.
- **Name the complement in the instructions.** The largest documented effect
  in the rule-induction literature: asking a player to find the rule for high
  scores *and* the rule for low scores roughly doubled solution rates in the
  classic experiment. Needs the oracle to report a category label.
- **Charge for wrong guesses** and print the running cost, so students design
  experiments instead of spraying guesses.
- **Ship worlds where the obvious guess is too broad and worlds where it is
  too narrow**, so students learn when positive testing works rather than
  concluding they are simply biased.
- **A browser version on GitHub Pages**, which is how this account already
  reaches people. Blocked on the oracle change, since a separate process does
  not exist in the browser.
- **Sandbox discovery through a declared entry point**, so a sandbox can live
  in someone else's repository later without a redesign.
- **A manifest schema that rejects unknown keys**, which is stricter than the
  current forgiving reader.

## Considered and rejected

**A Python floor of 3.11 or higher.** Recommended by the scientific Python
policy, and it would break the author's own machine, which ships 3.9. A
teaching tool whose promise is that nothing needs installing cannot open by
demanding a Python upgrade. The code stays compatible with 3.9, the metadata
says 3.9, and continuous integration tests the modern versions too. Revisit
when the student path is a browser, at which point the local Python version
stops mattering.

**Submitting to the Journal of Open Source Software now.** Not possible. It
requires six months of public history and evidence of research use, with
aspirational statements explicitly excluded. Mid-2027 at the earliest, and
pyOpenSci is the better first stop because it has no waiting period.

**Writing `paper.md` now.** The required sections have grown, so anything
drafted today would be drafted against a checklist that will have moved by the
time it can be submitted.

**A source layout.** Recommended by the packaging guides, and it would mean a
student cannot clone the repository and run it. Under a source layout the
package is not importable until it is installed, and the promise here is that
nothing needs installing. The real benefit of a source layout, catching a file
that works from the repository but is missing from the built package, is
bought instead by a continuous integration step that installs the package and
runs it from a different directory. Revisit if this is ever published to the
package index as the primary way people get it.

**A documentation site.** The readme still fits in one scroll. A site is
navigation a student has to learn before they reach the thing.

**Type checking as a blocking gate, coverage thresholds, code owners,
governance and funding files, pull request templates.** Solo-project ceremony.
Reviewers do not expect them at this size and they read as process theater.

**Containers for the oracle.** The correct answer for evaluating a capable
agent, and the wrong answer for a student's first ten minutes. The honest
move is the one taken: say in the readme exactly what the current wall does
and does not stop.

**Writing a general task standard.** Two serious attempts are archived and
point users elsewhere, and a third is in maintenance mode. The lesson is to
stay small and interoperate later.
