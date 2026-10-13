# A finished run, so you can read the output before running anything

`example-run/` is a real run of the `codon-lite` sandbox, played by the
`hillclimb` baseline: an investigator that keeps whatever scored best and
changes one character at random. It has no theory and never forms one.

Read the files in this order:

This run predates two changes: sandbox versions moved to the two-part form,
and an agent run no longer writes the hidden rule into its own folder. It is
kept as it was rather than regenerated, because a run record is a historical
document and editing one afterwards is exactly what the fingerprint exists to
detect.

1. **run.json** - it reached 5 out of a possible 6 in 40 rounds.
2. **judge.json** - and stated 0 of the 4 true claims about the hidden rule.
3. **notebook.md** - forty entries of "that was better, I kept it", which is
   what optimization without understanding looks like written down.
4. **answer_key.json** - what was actually going on, revealed only after the
   last round.

This pair of numbers is the whole argument for the framework. On a normal
benchmark, 5 out of 6 is a good score and would be the end of the report. Here
it sits next to a zero, and the zero is the more interesting number.

The random baseline is worse still, in a way that is worth seeing: it reaches 5
within five rounds by pure guessing. If blind guessing matches a careful search,
the score was never measuring the thing anyone cared about.

Any real investigator has to beat the hill climber on the second number, not
the first.
