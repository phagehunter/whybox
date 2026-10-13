"""The wall between the investigator and the answer key.

The oracle runs as its own operating-system process. The runner talks to it by
writing one line of JSON and reading one line of JSON back. That is the whole
protocol.

Why bother, when both halves are Python? Because a sandbox is only meaningful
if the hidden rule stays hidden. An AI agent that can import the oracle module
can read the rule straight out of it, and then the experiment measures nothing.
A separate process with a text pipe is a wall you can point at and explain.

Request lines look like:
    {"op": "describe"}
    {"op": "measure", "specimens": ["ACGT...", ...]}
    {"op": "answer_key"}            <- refused unless the server was started
                                       with --reveal, which the runner only
                                       does after the final round

Response lines look like:
    {"ok": true, "result": {...}}
    {"ok": false, "error": "...", "kind": "validation"}
"""

import json
from typing import Any, Dict

PROTOCOL_VERSION = 1


def encode(message: Dict[str, Any]) -> str:
    return json.dumps(message, separators=(",", ":")) + "\n"


def decode(line: str) -> Dict[str, Any]:
    return json.loads(line)


def ok(result: Any) -> Dict[str, Any]:
    return {"ok": True, "result": result, "v": PROTOCOL_VERSION}


def err(message: str, kind: str = "error") -> Dict[str, Any]:
    return {"ok": False, "error": str(message), "kind": kind, "v": PROTOCOL_VERSION}
