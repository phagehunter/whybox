# How this research was done

Written before the findings, so that the method can be judged separately from
the conclusions it produced. If the conclusions look convenient, check them
against this page.

## The question

The repository is about to be made public. The question is not "is the code
good" but a narrower one:

> What do comparable projects do that this one does not do yet, and which of
> those gaps would a reader notice first?

"Comparable" is doing real work in that sentence, so it is defined below
rather than left to taste.

## What counts as an adjacent project

Four families, chosen because each one shares a different edge with this
project. No single existing project shares all four, which is why four
searches were run rather than one.

| Thread | Shares with us | Why it was chosen |
|---|---|---|
| 1. Agent evaluation harnesses | the plugin format: outsiders add new tasks to a shared runner | They solved task packaging, isolation, and versioning years ago. Inventing our own would be arrogant. |
| 2. Scientific software standards | the repository itself: citable, reviewable, academic | There are published checklists. A repo that fails them looks unserious to exactly the audience we want. |
| 3. Rule-induction games and teaching delivery | the puzzle and the student | The hidden-rule game is old and well studied. Separately, students cannot install Python. |
| 4. Benchmark integrity and leaderboards | the published results | We promised a public leaderboard. Leaderboards fail in known, documented ways. |

Deliberately excluded: general Python style guides, which say nothing specific
to this project, and the original paper's own repository, which was already
read and credited and is not an independent source of convention.

## How the threads were run

Four independent searches, launched at the same time and not allowed to see
each other's results. This matters: a single search would have anchored on
whatever it found first, and the four families use different vocabulary for
the same idea. Running them blind to each other means an agreement between two
threads is real agreement rather than an echo.

Each thread was given the same three instructions:

1. **Prefer the primary source.** Read the actual repository file or the
   actual paper, not a blog post summarizing it. A convention is what projects
   do, not what commentary says they do.
2. **Cite a URL for every claim.** A finding without a link does not go in
   the register below, however plausible it sounds.
3. **Report what contradicts us.** Each thread was asked specifically for
   places where this project is off-convention and for traps the comparable
   projects fell into. A search that only returns agreement was run wrong.

## The organization's own conventions, checked first

Before looking outward, the account that will host this was examined, because
house style beats general best practice when the two conflict.

Findings: `github.com/phagehunter` is a user account, not an organization,
with 31 repositories. The pinned ones are static HTML sites. Two were read in
full. Both have no license, no description, no topics, no continuous
integration, and a one-line README. Both ship `.nojekyll` and `index.html`,
which is the layout of a GitHub Pages site.

Two conclusions follow, and both shaped the edit list:

- There is no house Python convention to match, because this would be the
  first Python package on the account. General best practice therefore wins by
  default.
- The house delivery mechanism is a static web page. That is a strong argument
  for a browser-playable version of the sandbox, and it is why thread 3 was
  asked specifically whether our sealed oracle design survives in a browser.

## How sources are kept

Every page opened is recorded in `2026-10-13-sources.md`, one row each, with
the thread that opened it and what it was used for. The register is the
audit trail: a claim in the findings that has no row there is unsupported and
should be treated as opinion.

Findings live in one file per thread, so that a weak thread can be thrown out
without disturbing the others.

## How a finding becomes an edit

A finding only becomes a change to this repository if it passes three tests:

1. **Recurrence or authority.** Either two independent threads found it, or
   one authoritative source requires it. One blog post recommending something
   is not enough.
2. **Proportion.** It has to make sense at this size. Much of what large
   benchmark projects do exists to handle scale and money we do not have, and
   copying it would be cargo cult rather than craft.
3. **It survives the stated audience.** The primary audience is
   undergraduates. A convention that serves maintainers at the cost of a
   student's first ten minutes loses.

Anything that fails a test is still written down, in the "considered and
rejected" section of the edit list, with the reason. A rejected idea with a
recorded reason is cheaper to revisit than one that was never written down.

## Known limits of this method

- The four threads were run by language models reading the web. They can
  misread a page. The source register exists so any claim can be checked.
- Recency is uneven. Conventions in this area move fast, and some sources will
  be a year or two old by the time they are read.
- Nothing here was tested against real students. Every claim about what a
  student will find hard is inference from the literature, not observation.
