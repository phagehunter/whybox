"""The experimental loop.

The runner is the referee. It starts the sealed oracle in its own process,
asks the investigator for a submission, passes it through the wall, hands the
report back, and writes everything down. It also enforces the two rules that
make runs comparable: a fixed number of rounds, and no peeking.

    loop for each round:
        investigator proposes specimens + says why
        oracle measures them and returns a report
        investigator reads the report and writes a notebook entry
    after the last round:
        investigator states its final theory
        runner unseals the answer key and saves it next to the notebook
"""

import glob
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

from whybox import protocol
from whybox.record import RunRecord, timestamp
from whybox.spec import SandboxSpec


class SealedOracleClient(object):
    """Talks to the oracle process over a pipe."""

    def __init__(self, directory: str, reveal: bool = False):
        command = [sys.executable, "-m", "whybox.sealed_server", directory]
        if reveal:
            command.append("--reveal")
        env = dict(os.environ)
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env["PYTHONPATH"] = repo_root + os.pathsep + env.get("PYTHONPATH", "")
        self.process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1, env=env,
            cwd=repo_root)

    def ask(self, message: Dict[str, Any]) -> Dict[str, Any]:
        assert self.process.stdin and self.process.stdout
        self.process.stdin.write(protocol.encode(message))
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError("the oracle process stopped responding.\n%s" % stderr)
        return protocol.decode(line)

    def close(self) -> None:
        try:
            self.ask({"op": "shutdown"})
        except Exception:  # noqa: BLE001 - shutting down anyway
            pass
        for stream in (self.process.stdin, self.process.stdout, self.process.stderr):
            try:
                if stream is not None:
                    stream.close()
            except Exception:  # noqa: BLE001
                pass
        try:
            self.process.wait(timeout=5)
        except Exception:  # noqa: BLE001
            try:
                self.process.kill()
            except Exception:  # noqa: BLE001
                pass


class Runner(object):
    def __init__(self, spec: SandboxSpec, agent: Any, runs_root: str = "runs",
                 rounds: Optional[int] = None, quiet: bool = False,
                 reveal_key: bool = True):
        self.spec = spec
        self.agent = agent
        self.rounds = rounds or spec.rounds
        self.quiet = quiet
        # Whether to write the hidden rule into this run's folder at the end.
        # Right for a person, who should see what they were up against. Wrong
        # for an agent with a shell, because run folders pile up and the next
        # run can read the last one's answer.
        self.reveal_key = reveal_key
        self.runs_root = runs_root
        label = "%s__%s__%s" % (spec.name, getattr(agent, "name", "agent"), timestamp())
        self.record = RunRecord(
            os.path.join(runs_root, label), spec.name,
            getattr(agent, "name", "agent"), self.rounds,
            metadata={"oracle_kind": spec.oracle_kind, "sandbox_version": spec.version})

    def _say(self, text: str) -> None:
        if not self.quiet:
            print(text, flush=True)

    def _warn_about_old_answer_keys(self) -> None:
        """Shout if a previous run left the answer lying around.

        This is the leak that matters in practice. An investigator with a
        shell does not need to break the sealed wall if an earlier run of the
        same sandbox already wrote the rule to disk next door.
        """
        pattern = os.path.join(self.runs_root, "%s__*" % self.spec.name,
                               "answer_key.json")
        stale = glob.glob(pattern)
        if stale:
            self._say(
                "WARNING: %d earlier run(s) of this sandbox left answer_key.json "
                "on disk, which an investigator with filesystem access can read. "
                "Move or delete %s before measuring anything you intend to "
                "publish." % (len(stale), os.path.dirname(stale[0])))

    def run(self) -> Dict[str, Any]:
        client = SealedOracleClient(self.spec.directory, reveal=False)
        history: List[Dict[str, Any]] = []
        best: Optional[float] = None
        status = "complete"

        try:
            self._warn_about_old_answer_keys()

            described = client.ask({"op": "describe"})
            public_facts = described.get("result", {}) if described.get("ok") else {}

            # Published before the first round: proof the rule cannot change
            # underneath the investigator, and that nobody can claim later
            # that they had it from the start.
            committed = client.ask({"op": "commitment"})
            commitment = (committed.get("result") or {}).get("sha256", "") \
                if committed.get("ok") else ""
            self.record.metadata["rule_commitment_sha256"] = commitment
            self._say("rule commitment: %s" % (commitment[:16] + "..." if commitment else "unavailable"))

            self.agent.begin(spec=self.spec,
                             instructions=self.spec.read_instructions(),
                             public_facts=public_facts,
                             rounds=self.rounds)
            self.record.append_notebook(
                "setup", "Public facts given to the investigator:\n\n```\n%s\n```"
                % public_facts)

            for index in range(1, self.rounds + 1):
                proposal = self.agent.propose(index, history)
                specimens = proposal.get("specimens", [])
                rationale = proposal.get("rationale", "")

                started = time.time()
                response = client.ask({"op": "measure", "specimens": specimens})
                elapsed = time.time() - started

                self.record.log_round(index, specimens, rationale, response, elapsed)

                if response.get("ok"):
                    report = response.get("result", {})
                    score = None
                    for value in (report.get("scores") or {}).values():
                        score = float(value)
                        break
                    if score is not None and (best is None or score > best):
                        best = score
                    self._say("round %3d/%d  score=%s  %s"
                              % (index, self.rounds,
                                 "n/a" if score is None else round(score, 4),
                                 rationale[:60]))
                else:
                    report = {"error": response.get("error"), "kind": response.get("kind")}
                    self._say("round %3d/%d  rejected: %s"
                              % (index, self.rounds, response.get("error", "")[:70]))

                history.append({"round": index, "specimens": specimens,
                                "rationale": rationale, "report": report,
                                "ok": bool(response.get("ok"))})

                entry = self.agent.observe(index, report, history)
                if entry:
                    self.record.append_notebook("round %d" % index, entry)
        except KeyboardInterrupt:
            status = "interrupted"
            self._say("\ninterrupted; the partial run is still on disk.")
        finally:
            client.close()

        final_theory = ""
        try:
            final_theory = self.agent.conclude(history) or ""
        except Exception as exc:  # noqa: BLE001
            final_theory = "the investigator failed to produce a final theory: %s" % exc

        # Only now does the answer key come out from behind the wall.
        reveal_client = SealedOracleClient(self.spec.directory, reveal=True)
        try:
            revealed = reveal_client.ask({"op": "answer_key"})
            if revealed.get("ok"):
                if self.reveal_key:
                    self.record.write_answer_key(revealed["result"])
                else:
                    self._say("the answer key was not written to this run folder "
                              "(use --reveal-key to write it)")
        finally:
            reveal_client.close()

        summary = self.record.finish(best, final_theory, status=status)
        self._say("\nrun folder: %s" % self.record.root)
        # The investigator has committed. Now it is allowed to know.
        self._say("the rule you were up against is in answer_key.json; read it "
                  "against your own notebook.md")
        return summary
