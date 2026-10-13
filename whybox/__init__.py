"""whybox: a small toolkit for building and running science sandboxes.

A science sandbox is a game with three pieces:

  specimens  - the things you can submit for testing (a DNA sequence, a
               protein, a chemical, or just a string of symbols)
  assay      - the measurement performed on a specimen
  oracle     - the sealed machine that runs the assay and hands back a report

An investigator (a person or an AI agent) submits specimens round after round,
reads the report, writes down what it now believes, and chooses what to try
next. The rules inside the oracle are hidden. The point is not only to get a
high score. The point is to work out why the score moves.

Nothing in this package knows anything about any particular science. A sandbox
author supplies the oracle; whybox supplies the loop, the record keeping,
and the sealed wall between the investigator and the answer key.
"""

__version__ = "0.1.0"

from whybox.spec import SandboxSpec, load_spec
from whybox.oracle import Oracle, Report

__all__ = ["SandboxSpec", "load_spec", "Oracle", "Report", "__version__"]
