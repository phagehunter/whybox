"""Investigators: the things that play in a sandbox.

An investigator can be a simple script, a person typing at a prompt, or a
large language model. The toolkit only cares that it answers four calls:

    begin(spec, instructions, public_facts, rounds)
    propose(round_index, history) -> {"specimens": [...], "rationale": "..."}
    observe(round_index, report, history) -> notebook text, or ""
    conclude(history) -> the final theory, in plain words

`human` is you at the keyboard, which is the fastest way to understand what a
sandbox is actually testing. The two scripted investigators exist so that a new
sandbox can be tested and given a floor to beat before any model is pointed at
it. `random` is the
floor: it guesses. `hillclimb` is the honest-but-dumb competitor: it keeps
whatever scored best and tweaks it, with no idea why anything works. If a
model cannot beat hill climbing, the sandbox has not learned anything about
the model. If it beats hill climbing on score but its notebook reads like hill
climbing, that is the finding the sandbox exists to surface.
"""

from whybox.agents.base import Agent
from whybox.agents.human import HumanAgent
from whybox.agents.scripted import RandomAgent, HillClimbAgent

#: name -> class, used by `whybox run --agent <name>`
REGISTRY = {
    "random": RandomAgent,
    "hillclimb": HillClimbAgent,
    "human": HumanAgent,
}

try:  # optional: needs the `anthropic` package and an API key
    from whybox.agents.claude_agent import ClaudeAgent
    REGISTRY["claude"] = ClaudeAgent
except Exception:  # noqa: BLE001 - absence is normal, not an error
    pass

__all__ = ["Agent", "RandomAgent", "HillClimbAgent", "HumanAgent", "REGISTRY"]
