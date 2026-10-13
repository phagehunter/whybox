"""You, at the keyboard.

A sandbox is a game, and the fastest way to understand what it is testing is
to play a few rounds of it yourself before pointing any model at it. Ten
rounds of guessing at a hidden rule teaches more about why the framework
separates score from understanding than any amount of reading.

    python -m whybox run codon-lite --agent human --rounds 15

Each round asks for a specimen and for a one-line reason. The reason is not
busywork: it goes in the notebook, and at the end you get graded on your
stated theory exactly as a model would be. Press Enter on an empty specimen to
be given a random one, which is a fair way to start when you know nothing.
"""

import random
import sys
from typing import Any, Dict, List, Optional

from whybox.agents.base import Agent


class HumanAgent(Agent):
    name = "human"

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def begin(self, spec: Any, instructions: str, public_facts: Dict[str, Any],
              rounds: int) -> None:
        Agent.begin(self, spec, instructions, public_facts, rounds)
        if not sys.stdin.isatty():
            raise RuntimeError(
                "the human investigator needs a keyboard; this looks like a script "
                "or a continuous integration run. Use --agent random or --agent "
                "hillclimb instead.")
        print("\n" + "=" * 70)
        print(instructions.strip() or spec.title)
        print("=" * 70)
        print("\nWhat you are told about this world:\n")
        for key, value in public_facts.items():
            print("  %-20s %s" % (key, value))
        print("\nYou have %d experiments. Empty specimen means 'pick one at random'."
              % rounds)
        print("=" * 70 + "\n")

    def propose(self, round_index: int, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        alphabet = self.facts.get("alphabet", "ACGT")
        length = int(self.facts.get("specimen_length", 24))
        print("\n--- experiment %d of %d ---" % (round_index, self.rounds))
        specimen = input("specimen (%d characters from %s): "
                         % (length, alphabet)).strip().upper()
        if not specimen:
            specimen = "".join(self.rng.choice(alphabet) for _ in range(length))
            print("  using a random one: %s" % specimen)
        rationale = input("what does this test? ").strip() or "(no reason given)"
        return {"specimens": [specimen], "rationale": rationale}

    def observe(self, round_index: int, report: Dict[str, Any],
                history: List[Dict[str, Any]]) -> Optional[str]:
        if "error" in report:
            print("  rejected: %s" % report["error"])
            print("  (that did not cost you an experiment's worth of information)")
            return None
        for name, value in (report.get("scores") or {}).items():
            print("  %s = %s" % (name, value))
        note = input("notebook (what do you now think the rule is?) ").strip()
        return note or None

    def conclude(self, history: List[Dict[str, Any]]) -> str:
        print("\n" + "=" * 70)
        print("Experiments finished. State the rule in plain words, specific enough")
        print("that someone else could predict the score of a sequence you never")
        print("tried. 'I do not know' is a better answer than a confident guess.")
        print("=" * 70)
        lines: List[str] = []
        print("(blank line to finish)")
        while True:
            line = input("> ")
            if not line.strip():
                break
            lines.append(line)
        return "\n".join(lines)
