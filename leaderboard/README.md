# Results

Two baseline rows, so the table is not empty and so its shape is obvious at a
glance.

```
codon-lite, results version 1
investigator runs         score   insight graded by    status
-------------------------------------------------------------
random       1, single run     6.0      0/4  rubric       unverified
hillclimb    1, single run     5.0      0/4  rubric       unverified
```

Random guessing reaches the ceiling. A careful hill climb does not quite. And
neither states a single true thing about the rule that produced the number.
If blind guessing beats a systematic search, the score column was never
measuring the thing anyone cared about.

The heading says "results version 1" rather than naming the exact sandbox
version, because a letter bump means the interface changed and the scores did
not. Rows from `1-A` and `1-B` belong in the same table. Rows from `2-A` would
not.

## The floor that is not in the table

`python -m whybox audit codon-lite` writes a notebook containing the
answer key's vocabulary, runs no experiments at all, and collects **4 of 4**
on the understanding column.

That number is the floor. It is not a row here because it is not a run, but
any understanding score produced by word matching has to be read against it.
A sandbox whose audit says four out of four is a sandbox whose second column
means nothing until a person or a second model reads the notebook.

## How a row is ranked

Sorted by understanding, then a reproduced row over an unverified one, then a
human grade over a model grade over word matching, then score, then fewer
rounds used. The tie-break is published because an undefined secondary sort
quietly becomes the real ranking, and anything that ranks gets gamed.

A row must clear a quarter of the sandbox's ceiling before its understanding
is ranked at all. Without that floor, an investigator that runs no experiment
and writes a confident notebook tops a board sorted on understanding.

Rows from different sandbox versions sit in separate tables and are never
interleaved. A score from before the hidden rule changed cannot be compared
with one from after.

## Adding a row

```bash
python -m whybox export runs/<folder> --append
python -m whybox table
```

Every row starts as `unverified`, which means nobody has checked it. The
format, and what a published leaderboard would need beyond a local file, is in
[docs/leaderboard.md](../docs/leaderboard.md).
