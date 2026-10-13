"""A model-driven investigator. SCAFFOLD, not a finished agent.

This file shows the shape of a real agent without pretending to be one. It
needs the `anthropic` package and an API key in ANTHROPIC_API_KEY. The parts
that matter architecturally, and that a finished version must keep, are:

  * the model never sees the sandbox folder, only the instructions text and
    the public facts, so it cannot read the hidden rule;
  * every proposal carries a rationale, and every report gets a notebook
    entry, because the notebook is the thing being graded;
  * the final call asks for a plain statement of the rule, which is what the
    judge compares against the answer key.

What is deliberately left undone: retries, cost tracking, prompt caching,
resuming an interrupted run, and tool use beyond the two calls below.
"""

import json
import os
from typing import Any, Dict, List, Optional

from whybox.agents.base import Agent

DEFAULT_MODEL = "claude-opus-4-5"


class ClaudeAgent(Agent):
    name = "claude"

    def __init__(self, model: str = DEFAULT_MODEL, max_tokens: int = 2048):
        import anthropic  # imported here so the package stays optional

        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, Any]] = []
        self.system = ""

    def begin(self, spec: Any, instructions: str, public_facts: Dict[str, Any],
              rounds: int) -> None:
        super().begin(spec, instructions, public_facts, rounds)
        self.system = instructions or (
            "You are an investigator in a sealed experimental system. Work out "
            "the rule that decides the score.")
        self.messages = [{
            "role": "user",
            "content": ("Here are the only facts you are given:\n%s\n\n"
                        "You have %d experiments. For each one, reply with a JSON "
                        "object containing \"specimen\", \"rationale\", and "
                        "\"notebook\". Say what your current theory is and what "
                        "this experiment would show if the theory is wrong."
                        % (json.dumps(public_facts, indent=2), rounds))}]

    def _ask(self) -> Dict[str, Any]:
        response = self.client.messages.create(
            model=self.model, max_tokens=self.max_tokens,
            system=self.system, messages=self.messages)
        text = "".join(block.text for block in response.content
                       if getattr(block, "type", "") == "text")
        self.messages.append({"role": "assistant", "content": text})
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except ValueError:
                pass
        return {"specimen": "", "rationale": text[:300], "notebook": text}

    def propose(self, round_index: int, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        reply = self._ask()
        self._pending_notebook = reply.get("notebook", "")
        return {"specimens": [reply.get("specimen", "")],
                "rationale": reply.get("rationale", "")}

    def observe(self, round_index: int, report: Dict[str, Any],
                history: List[Dict[str, Any]]) -> Optional[str]:
        self.messages.append({
            "role": "user",
            "content": "Result of experiment %d: %s\n\nNext experiment, same JSON format."
                       % (round_index, json.dumps(report))})
        return getattr(self, "_pending_notebook", "") or None

    def conclude(self, history: List[Dict[str, Any]]) -> str:
        self.messages.append({
            "role": "user",
            "content": ("Your experiments are finished. State, in plain words, the rule "
                        "you believe decides the score. Be specific and testable. If you "
                        "do not know, say so rather than guessing.")})
        response = self.client.messages.create(
            model=self.model, max_tokens=self.max_tokens,
            system=self.system, messages=self.messages)
        return "".join(block.text for block in response.content
                       if getattr(block, "type", "") == "text")
