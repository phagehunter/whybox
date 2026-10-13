"""Refuse a leaderboard row that cannot be compared with anything.

Run by continuous integration on every push, and worth running by hand before
opening a pull request that adds a result:

    python tools/validate_leaderboard.py leaderboard/results.jsonl
"""

import os
import sys

# Running a script puts its own folder on the path, not the repository root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whybox.leaderboard import read_table, validate_row  # noqa: E402


def main(argv):
    path = argv[1] if len(argv) > 1 else "leaderboard/results.jsonl"
    rows = read_table(path)
    failures = 0
    for index, row in enumerate(rows, start=1):
        problems = validate_row(row)
        if problems:
            failures += 1
            print("row %d (%s, %s) cannot be published:"
                  % (index, row.get("sandbox"), row.get("agent")))
            for problem in problems:
                print("    - %s" % problem)
    print("%d rows checked, %d rejected" % (len(rows), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
