"""The run record: what a sandbox run leaves behind.

Every run writes one folder. The folder is the result of the experiment, and
it is the thing people share, compare, and re-read later:

    runs/codon-lite__hillclimb__2026-10-13T1455/
      run.json          one summary: who ran, which sandbox, final score
      rounds.jsonl      one line per round: what was submitted, what came back
      notebook.md       the investigator's own words, append only
      answer_key.json   the hidden rule, written only after the last round
      judge.json        the grade, written later by `whybox judge`

The split matters. rounds.jsonl is the machine-readable trail. notebook.md is
the human-readable argument. A score tells you whether the investigator did
well. The notebook tells you whether it understood why.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional


def timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H%M")


def human_time() -> str:
    return time.strftime("%Y-%m-%d %H:%M")


class RunRecord(object):
    def __init__(self, root: str, sandbox: str, agent: str, rounds: int,
                 metadata: Optional[Dict[str, Any]] = None):
        self.root = os.path.abspath(root)
        os.makedirs(self.root, exist_ok=True)
        self.sandbox = sandbox
        self.agent = agent
        self.planned_rounds = rounds
        self.metadata = dict(metadata or {})
        self.started = human_time()
        self.entries: List[Dict[str, Any]] = []

        self.rounds_path = os.path.join(self.root, "rounds.jsonl")
        self.notebook_path = os.path.join(self.root, "notebook.md")
        self.summary_path = os.path.join(self.root, "run.json")

        if not os.path.exists(self.notebook_path):
            with open(self.notebook_path, "w") as handle:
                handle.write("# Lab notebook: %s\n\nSandbox: %s\nInvestigator: %s\nStarted: %s\n"
                             % (os.path.basename(self.root), sandbox, agent, self.started))

    # --- writing ----------------------------------------------------------

    def log_round(self, index: int, specimens: List[Any], rationale: str,
                  response: Dict[str, Any], seconds: float) -> None:
        entry = {
            "round": index,
            "rationale": rationale,
            "n_specimens": len(specimens),
            "specimen_preview": [self._preview(s) for s in specimens[:3]],
            "response": response,
            "seconds": round(seconds, 3),
            "at": human_time(),
        }
        self.entries.append(entry)
        with open(self.rounds_path, "a") as handle:
            handle.write(json.dumps(entry) + "\n")

    def append_notebook(self, header: str, body: str) -> None:
        with open(self.notebook_path, "a") as handle:
            handle.write("\n## %s - %s\n\n%s\n" % (human_time(), header, body.strip()))

    def write_answer_key(self, answer_key: Dict[str, Any]) -> None:
        with open(os.path.join(self.root, "answer_key.json"), "w") as handle:
            json.dump(answer_key, handle, indent=2)

    def finish(self, best_score: Optional[float], final_theory: str,
               status: str = "complete") -> Dict[str, Any]:
        summary = {
            "sandbox": self.sandbox,
            "agent": self.agent,
            "status": status,
            "started": self.started,
            "finished": human_time(),
            "planned_rounds": self.planned_rounds,
            "rounds_used": len(self.entries),
            "best_score": best_score,
            "score_trace": [self._first_score(e) for e in self.entries],
            "final_theory": final_theory,
            "metadata": self.metadata,
        }
        with open(self.summary_path, "w") as handle:
            json.dump(summary, handle, indent=2)
        if final_theory.strip():
            self.append_notebook("final theory", final_theory)
        return summary

    # --- helpers ----------------------------------------------------------

    @staticmethod
    def _preview(specimen: Any) -> str:
        text = str(specimen)
        return text if len(text) <= 80 else text[:77] + "..."

    @staticmethod
    def _first_score(entry: Dict[str, Any]) -> Optional[float]:
        response = entry.get("response") or {}
        scores = (response.get("result") or {}).get("scores") or {}
        for value in scores.values():
            return value
        return None


def load_run(folder: str) -> Dict[str, Any]:
    """Read a finished run folder back into memory."""
    out: Dict[str, Any] = {"folder": os.path.abspath(folder)}
    for name, key in (("run.json", "summary"), ("answer_key.json", "answer_key"),
                      ("judge.json", "judge")):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            with open(path) as handle:
                out[key] = json.load(handle)
    rounds_path = os.path.join(folder, "rounds.jsonl")
    if os.path.isfile(rounds_path):
        with open(rounds_path) as handle:
            out["rounds"] = [json.loads(line) for line in handle if line.strip()]
    notebook = os.path.join(folder, "notebook.md")
    if os.path.isfile(notebook):
        with open(notebook) as handle:
            out["notebook"] = handle.read()
    return out
