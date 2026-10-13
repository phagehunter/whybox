# Versioning

Two different things carry versions here, and conflating them is how
benchmarks quietly stop meaning anything.

## The toolkit

Ordinary [semantic versioning](https://semver.org/). Nothing unusual.

## A sandbox

Two parts, like `1-A`.

**The number rises when old scores stop being comparable.** The hidden rule
changed, the report changed, the round budget changed, or a bug fix moved the
numbers. Anyone holding a score from before the bump is holding a number that
can no longer be put beside a new one.

**The letter rises when only the interface changed.** A renamed setting, a new
required field, a different command. Old scores are still fine; old commands
are not.

Neither part ever resets, and neither can be reused.

## Why two parts rather than one

"Your old score is meaningless" and "your old command no longer runs" are
different emergencies, and a single number cannot say which has happened. The
convention is borrowed from the most actively maintained evaluation harness in
this field, which arrived at it the hard way.

## The rule that is easy to break by accident

**A fix to a hidden rule is a number bump, even when it is obviously a bug
fix.** This is the one people get wrong: the change felt like a correction, so
the version stayed, and now two incomparable scores sit in one table looking
comparable.

If you are unsure whether a change moves scores, run the baselines before and
after. If any number moves, bump the number.

## What the toolkit enforces

- A version that is not in `N-X` form is refused, with an explanation.
- Every run records the sandbox version and a hash of the hidden rule.
- The results table groups rows by version and never interleaves them.

## What it cannot enforce

It cannot tell that you changed a rule and left the version alone. That check
would require storing a hash of the sealed folder with each released version
and comparing on every run. It is not built. Until it is, the version is a
promise made by the sandbox author, and the hash recorded in each run is the
evidence that can later show the promise was broken.
