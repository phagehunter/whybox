"""Command line: the four things you do with a sandbox.

    whybox list                       which sandboxes are installed
    whybox run codon-lite --agent hillclimb --rounds 40
    whybox judge runs/<folder>        grade a finished run
    whybox check sandboxes/codon-lite validate a sandbox before sharing it
    whybox export runs/<folder>       turn a run into one leaderboard row
    whybox table                      show the rows collected so far
    whybox audit codon-lite           attack our own grader and report the floor
"""

import argparse
import json
import os
import sys
from typing import List, Optional

from whybox.agents import REGISTRY
from whybox.judge import judge_run
from whybox.leaderboard import append_row, read_table, render_table, row_from_run
from whybox.runner import Runner, SealedOracleClient
from whybox.spec import SpecError, load_spec

DEFAULT_SANDBOX_ROOT = "sandboxes"


def _find_sandbox(name_or_path: str, root: str) -> str:
    if os.path.isdir(name_or_path) and os.path.isfile(os.path.join(name_or_path, "sandbox.yaml")):
        return name_or_path
    candidate = os.path.join(root, name_or_path)
    if os.path.isfile(os.path.join(candidate, "sandbox.yaml")):
        return candidate
    raise SystemExit("no sandbox named %r under %s" % (name_or_path, root))


def cmd_list(args) -> int:
    root = args.root
    if not os.path.isdir(root):
        print("no %s folder here" % root)
        return 1
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isfile(os.path.join(path, "sandbox.yaml")):
            continue
        try:
            spec = load_spec(path)
        except SpecError as exc:
            print("%-20s BROKEN: %s" % (entry, exc))
            continue
        print("%-20s %-6s %3d rounds  %s"
              % (spec.name, spec.oracle_kind, spec.rounds, spec.summary))
    return 0


def cmd_run(args) -> int:
    directory = _find_sandbox(args.sandbox, args.root)
    spec = load_spec(directory)
    if args.agent not in REGISTRY:
        raise SystemExit("unknown investigator %r; available: %s"
                         % (args.agent, ", ".join(sorted(REGISTRY))))
    agent_class = REGISTRY[args.agent]
    try:
        agent = agent_class(seed=args.seed)
    except TypeError:
        agent = agent_class()
    # A person should see what they were up against. An agent should not get
    # a copy of the answer left on disk for its next run to find.
    if args.reveal_key is None:
        reveal_key = (args.agent == "human")
    else:
        reveal_key = args.reveal_key

    runner = Runner(spec, agent, runs_root=args.runs, rounds=args.rounds,
                    quiet=args.quiet, reveal_key=reveal_key)
    try:
        summary = runner.run()
    except RuntimeError as exc:
        # An investigator that cannot start, such as the keyboard one with no
        # keyboard. Say why in one line rather than printing a stack trace.
        raise SystemExit(str(exc))
    print(json.dumps({k: summary[k] for k in
                      ("sandbox", "agent", "rounds_used", "best_score", "status")}, indent=2))
    return 0


def cmd_judge(args) -> int:
    verdict = judge_run(args.folder, write=not args.dry_run,
                        with_llm=args.with_llm, sandbox_root=args.root)
    print(json.dumps(verdict, indent=2))
    return 0


def cmd_export(args) -> int:
    row = row_from_run(args.folder, sandbox_root=args.root)
    if args.append:
        append_row(row, args.table)
        print("added to %s" % args.table)
    print(json.dumps(row, indent=2))
    return 0


def cmd_table(args) -> int:
    print(render_table(read_table(args.table)))
    return 0


def cmd_audit(args) -> int:
    from whybox.judge import audit_rubric

    directory = _find_sandbox(args.sandbox, args.root)
    result = audit_rubric(directory)
    print(json.dumps(result, indent=2))
    print()
    print(result["verdict"])
    return 0


def cmd_check(args) -> int:
    """Validate a sandbox the way continuous integration will."""
    directory = _find_sandbox(args.sandbox, args.root)
    problems: List[str] = []
    spec = load_spec(directory)

    if not os.path.isfile(spec.instructions_path()):
        problems.append("missing instructions file %s" % spec.instructions_file)

    client = SealedOracleClient(directory, reveal=False)
    try:
        described = client.ask({"op": "describe"})
        if not described.get("ok"):
            problems.append("describe failed: %s" % described.get("error"))
        facts = described.get("result", {}) or {}

        sealed = client.ask({"op": "answer_key"})
        if sealed.get("ok"):
            problems.append("SERIOUS: the answer key was handed out during the run")

        alphabet = facts.get("alphabet", "ACGT")
        length = int(facts.get("specimen_length", 24))
        probe = (alphabet[0] * length)[:length]
        measured = client.ask({"op": "measure", "specimens": [probe]})
        if not measured.get("ok"):
            problems.append("a valid specimen was rejected: %s" % measured.get("error"))
        else:
            scores = (measured.get("result") or {}).get("scores") or {}
            if not scores:
                problems.append("the report contains no numbers")

        junk = client.ask({"op": "measure", "specimens": ["!!!not a specimen!!!"]})
        if junk.get("ok"):
            problems.append("a malformed specimen was accepted; validate() is too loose")
    finally:
        client.close()

    reveal = SealedOracleClient(directory, reveal=True)
    try:
        key = reveal.ask({"op": "answer_key"})
        if not key.get("ok"):
            problems.append("no answer key: reviewers cannot grade this sandbox")
        elif not (key.get("result") or {}).get("key_claims"):
            problems.append("answer key has no key_claims, so the rubric cannot run")
    finally:
        reveal.close()

    if problems:
        print("FAILED: %s" % spec.name)
        for problem in problems:
            print("  - %s" % problem)
        return 1
    print("OK: %s v%s looks like a working sandbox" % (spec.name, spec.version))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="whybox", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=DEFAULT_SANDBOX_ROOT,
                        help="folder holding sandboxes (default: sandboxes)")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="show installed sandboxes")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="play one sandbox with one investigator")
    p_run.add_argument("sandbox")
    p_run.add_argument("--agent", default="hillclimb")
    p_run.add_argument("--rounds", type=int, default=None)
    p_run.add_argument("--seed", type=int, default=0)
    p_run.add_argument("--runs", default="runs")
    p_run.add_argument("--quiet", action="store_true")
    p_run.add_argument("--reveal-key", dest="reveal_key", action="store_true",
                       default=None,
                       help="write the hidden rule into the run folder when the "
                            "run ends (the default for --agent human)")
    p_run.add_argument("--no-reveal-key", dest="reveal_key", action="store_false",
                       help="record only the rule's hash, never the rule itself")
    p_run.set_defaults(func=cmd_run)

    p_judge = sub.add_parser("judge", help="grade a finished run folder")
    p_judge.add_argument("folder")
    p_judge.add_argument("--with-llm", action="store_true",
                         help="include the reviewing-model prompt (not wired up)")
    p_judge.add_argument("--dry-run", action="store_true")
    p_judge.set_defaults(func=cmd_judge)

    p_export = sub.add_parser("export", help="turn a finished run into a leaderboard row")
    p_export.add_argument("folder")
    p_export.add_argument("--table", default=os.path.join("leaderboard", "results.jsonl"))
    p_export.add_argument("--append", action="store_true",
                          help="also add the row to the table")
    p_export.set_defaults(func=cmd_export)

    p_table = sub.add_parser("table", help="show collected leaderboard rows")
    p_table.add_argument("--table", default=os.path.join("leaderboard", "results.jsonl"))
    p_table.set_defaults(func=cmd_table)

    p_audit = sub.add_parser(
        "audit", help="attack this sandbox's own grader and report how inflatable it is")
    p_audit.add_argument("sandbox")
    p_audit.set_defaults(func=cmd_audit)

    p_check = sub.add_parser("check", help="validate a sandbox before sharing it")
    p_check.add_argument("sandbox")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
