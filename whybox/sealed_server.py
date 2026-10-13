"""Runs one sandbox's oracle as a separate process.

Started by the runner, not by hand:

    python -m whybox.sealed_server <sandbox_directory> [--reveal]

It reads JSON request lines on standard input and writes JSON response lines
on standard output. `--reveal` permits the `answer_key` request, and the
runner passes it only after the investigator's last round is finished.
"""

import argparse
import importlib.util
import os
import sys
import traceback

from whybox import protocol
from whybox.oracle import ValidationError
from whybox.spec import load_spec


def _import_oracle_module(directory: str, module_name: str):
    path = os.path.join(directory, module_name + ".py")
    if not os.path.isfile(path):
        raise SystemExit("no %s.py in %s" % (module_name, directory))
    spec = importlib.util.spec_from_file_location(
        "sandbox_oracle_%s" % os.path.basename(directory).replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    # The sandbox folder goes on the path so the oracle can import its own
    # helper files, including the ones in sealed/.
    sys.path.insert(0, directory)
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run a sealed sandbox oracle.")
    parser.add_argument("directory")
    parser.add_argument("--reveal", action="store_true",
                        help="allow the answer_key request (post-run only)")
    args = parser.parse_args(argv)

    spec = load_spec(args.directory)
    module = _import_oracle_module(args.directory, spec.oracle_module)
    oracle_class = getattr(module, spec.oracle_class)
    oracle = oracle_class(args.directory, spec.data.get("oracle_config", {}))

    out = sys.stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = protocol.decode(line)
        except ValueError as exc:
            out.write(protocol.encode(protocol.err("bad JSON: %s" % exc, "protocol")))
            out.flush()
            continue

        op = request.get("op")
        try:
            if op == "describe":
                response = protocol.ok(oracle.describe())
            elif op == "measure":
                report = oracle.run_round(request.get("specimens", []))
                response = protocol.ok(report.to_dict())
            elif op == "commitment":
                # Always allowed. A hash is not the answer.
                response = protocol.ok({"sha256": oracle.commitment()})
            elif op == "answer_key":
                if not args.reveal:
                    response = protocol.err(
                        "the answer key is sealed during the run", "sealed")
                else:
                    response = protocol.ok(oracle.answer_key())
            elif op == "shutdown":
                out.write(protocol.encode(protocol.ok("bye")))
                out.flush()
                return 0
            else:
                response = protocol.err("unknown op %r" % op, "protocol")
        except ValidationError as exc:
            response = protocol.err(str(exc), "validation")
        except Exception as exc:  # noqa: BLE001 - report, never crash the wall
            response = protocol.err(
                "oracle failed: %s\n%s" % (exc, traceback.format_exc()), "oracle")

        out.write(protocol.encode(response))
        out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
