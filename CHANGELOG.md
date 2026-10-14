# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [semantic versioning](https://semver.org/).

Sandboxes carry their own separate two-part versions, explained in
[the versioning policy](docs/versioning.md).

## [Unreleased]

### Added

- `whybox audit`, which attacks this project's own word-matching grader
  and reports how much of a sandbox's understanding score a notebook full of
  keywords collects without running any experiment. For the example sandbox,
  all of it.
- A commitment hash of the hidden rule, printed before the first round and
  recorded in every run, so the rule provably cannot change mid-game.
- Canary strings in sealed data and answer keys, so that a later leak into
  training data becomes detectable.
- `--reveal-key` and `--no-reveal-key` on `run`.
- A warning when an earlier run of the same sandbox left its answer key on
  disk where a later run could read it.
- A published tie-break for leaderboard ranking, and a minimum score before a
  row is ranked by understanding at all.
- Result rows now carry status, submitter, artifact link, run count, selection
  rule, grader version, toolkit version, whether a person was in the loop, and
  a contamination declaration.
- Community files: contributing guide, code of conduct, security policy, issue
  templates.
- A written research review of adjacent projects, under `docs/research/`.
- A playable page at `index.html`, published at curtishoffmann.com/whybox. It
  reimplements the example world in JavaScript, since a browser has no
  subprocesses, and shows a fingerprint of the hidden rule before play starts
  so the rule provably cannot change mid-game.
- Tests that run both implementations and compare them, both on scores and on
  how they grade a stated rule, so the two cannot drift apart.

### Changed

- **Renamed from `sandboxkit` to `whybox`.** The old name was taken on the
  Python package index by a tool for sandboxing untrusted code, and the two
  meanings of "sandbox" sat one search result apart. The command, the module,
  and the canary marker all changed with it. The example sandbox went to
  `1-B`: a letter bump, because the interface moved and the scores did not.
- **The answer key is no longer written into an agent's run folder.** It is
  written only when the investigator is a person. Every run records the key's
  hash instead. Run folders accumulate, and an agent with a shell could read
  the rule out of an earlier run.
- Grading now fetches the answer key from the sandbox rather than the run
  folder, so the grader holds the key and the graded does not.
- Sandbox versions use a two-part form such as `1-A`. The number rises when
  old scores stop being comparable; the letter rises when only the interface
  changes. An old three-part version is now refused with an explanation.
- The results table groups rows by sandbox version instead of interleaving
  them.

### Fixed

- The grading vocabulary punished anyone who understood the system and said so
  in their own words. A correct plain-English statement scored zero of four.
  Both graders now recognize ordinary phrasings, and a test pins that.
- Submitting an empty rule on the web page destroyed the results markup, so
  the student could never see their own verdict afterwards.

### Known limits

- The understanding score is word matching and is fully inflatable. The audit
  command exists to make that measurable rather than deniable.
- The sealed wall is a process boundary, not a security boundary.
- Results are single runs. Reporting a spread over several seeds is not built.
