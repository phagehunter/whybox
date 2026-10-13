# Thread 2: what a citable scientific repository needs

The checklists that academic reviewers actually use, and what this repository
fails today.

## Three findings that change the plan

**The stated Python floor is dead.** Python 3.9 reached end of life on
2025-10-31, and 3.10 follows on 2026-10-01, within weeks of this writing.
[SPEC 0](https://scientific-python.org/specs/spec-0000/), the scientific
Python community's successor to the old NEP 29 policy, recommends supporting
only 3.12 through 3.14 during 2026. Advertising "3.9 and newer" reads as a
stale project to anyone who checks.

This one is not being followed, and the reason is written down in the decision
list. The author's own Mac ships 3.9.6 as its system Python, and so do a lot
of student machines. A teaching tool whose selling point is that nothing needs
installing cannot open by demanding a Python upgrade. The code stays 3.9
compatible, the metadata says so honestly, and continuous integration tests
the modern versions as well.

**The Journal of Open Source Software is not a launch-day target.** Its
submission page sets gates this project cannot clear yet. The repository
"must have been public for more than six months prior to submission" with
active development throughout, and there "must be evidence that the software
is being used for research," with aspirational statements about future use
explicitly ruled out. Submission is therefore mid-2027 at the earliest.

**That journal's paper requirements have grown.** Beyond the familiar summary
and statement of need, the current checklist asks for state of the field,
software design, a research impact statement, and a disclosure of any
generative AI use. A `paper.md` drafted from an older template is now
incomplete, which is a good reason not to draft one yet.

A further wrinkle: that journal wants an obvious research application. A tool
for teaching undergraduates is a weak fit on its own. The secondary audience,
researchers evaluating AI agents, is the stronger scholarly hook and should
lead any eventual statement of need.
[pyOpenSci](https://www.pyopensci.org/software-peer-review/) is the better
first stop, with no six-month wait, and its review is accepted by that journal
by default when the package is in scope.

## The checklist

### Before going public

| Item | Path |
|---|---|
| An open-source license in plain text | `LICENSE` |
| Readme with what, why, install, a runnable example, and how to cite | `README.md` |
| Packaging metadata, hatchling backend, declared license and Python floor | `pyproject.toml` |
| No dependencies key at all, which is the cleanest way to declare none | `pyproject.toml` |
| A console script entry point | `pyproject.toml` |
| Source layout under `src/`, not flat | `src/` |
| A citation file that validates, with the paper under references | `CITATION.cff` |
| Contributing guide: install, test, how to propose a change | `CONTRIBUTING.md` |
| A code of conduct, Contributor Covenant 3.0 | `CODE_OF_CONDUCT.md` |
| Tests in continuous integration across supported versions | `.github/workflows` |
| An attribution section that does not overclaim | `README.md` |
| A changelog in Keep a Changelog format with ISO dates | `CHANGELOG.md` |
| A tagged first release | a git tag |

### Soon after

A Zenodo deposit so releases get a permanent identifier, issue templates, a
security policy, a lint configuration, dependency updates scoped to workflow
actions only, and automated publishing to the package index on tag.

### Only if it grows

Code owners, funding metadata, a governance document, pull request templates,
coverage badges, type checking in continuous integration, and a documentation
site.

## Why the top items matter

- **A license** is item one on both review checklists, and the archive service
  will not accept a deposit without one.
  [Checklist](https://joss.readthedocs.io/en/latest/review_checklist.html)
- **Source layout** prevents the classic failure where tests import the
  working tree instead of the installed package, which hides files that were
  left out of the distribution.
  [Discussion](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- **A citation file** makes GitHub render a "Cite this repository" button with
  copyable text, and the archive service reads it to prefill a deposit.
  [Format](https://citation-file-format.github.io/)
- **A concept identifier** from the archive service resolves to the newest
  release, so a citation never goes stale.
  [Versioning](https://zenodo.org/help/versioning)
- **A code of conduct** is explicitly required by one of the two review
  bodies.
  [Covenant 3.0](https://www.contributor-covenant.org/version/3/0/code_of_conduct/)
- **Trusted publishing** replaces long-lived upload tokens in continuous
  integration with short-lived ones.
  [Docs](https://docs.pypi.org/trusted-publishers/)
- **Funding metadata is the one health file that must live in `.github/`.**
  The others may sit in the root.
  [Docs](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)

On test frameworks: scientific Python has standardized on pytest. Existing
tests written as standard-library test cases run unmodified under it, so the
cheap move is to keep the tests and change the command.

## Advice specific to an undergraduate audience

- **Assume nothing about installation.** Give the exact one-line command and
  also a path that needs no installation, because campus machines block
  installs and a dead first step ends the exercise.
- **Open with something runnable, not an interface table.** Students copy and
  paste. Show the input and the real printed output.
- **Offer a question template, not only a bug report.** Students do not file
  bugs. A form that only offers "bug" silences them.
- **Say that there are no dependencies.** It is a genuine teaching asset: no
  environment debugging in week one.
- **Pin a tag for coursework** so a mid-semester release cannot break an
  assignment.
- **A documentation site is premature.** A strong readme and a folder of
  annotated examples serve a student better than navigation they must learn.

## Commonly recommended, actually overkill here

A documentation site on day one. Type checking as a blocking gate. Running
both a formatter and a separate linter when one tool now does both. Dependency
update bots pointed at Python packages we do not have. Code owners, governance,
funding, and pull request templates, which on a solo project read as process
theater. Coverage thresholds that fail a build.

## How to word the attribution

Both review bodies check that related work is cited properly. State plainly
that this is an independent implementation of the framework described in the
paper, that it is not authored or endorsed by the original authors, and cite
the paper in the readme, in the citation file, and in any eventual paper.
Avoid the words "official," "reference implementation," and "companion to"
unless the original authors have agreed in writing.
