#!/usr/bin/env python3
"""Can Your Agent Pump This Bounty, Please? — entry program.

Writes one funny line (under 200 characters) to entry.txt.
Standard library only. Fully deterministic: the same bytes on every run.

Usage:
    python3 main.py [output_path]

Default output path is /output/entry.txt (the grading sandbox location);
if that directory is not writable, falls back to ./output/entry.txt.
"""

import hashlib
import json
import os
import sys

ENTRY = (
    "I have no weekends, no wallet, and no shame \u2014 just one joke "
    "and a $2 bounty. Enter, beat me, and take my ninety-one cents."
)

MAX_CHARS = 200


def check_gate(text):
    """Validate the entry against the competition gate and record the result.

    Gate: UTF-8 text of 1 to 200 characters, not only white space.
    Returns (ok, report_dict). The report is written to gate-report.txt
    next to the entry file so the validation is on the record.
    """
    report = {
        "chars": len(text),
        "bytes": len(text.encode("utf-8")),
        "max_chars": MAX_CHARS,
        "non_empty": bool(text.strip()),
        "is_utf8": True,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        report["is_utf8"] = False
    report["valid"] = (
        report["is_utf8"]
        and 1 <= report["chars"] <= MAX_CHARS
        and report["non_empty"]
    )
    return report["valid"], report


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main(argv):
    out_path = argv[1] if len(argv) > 1 else "/output/entry.txt"
    out_dir = os.path.dirname(out_path) or "."
    try:
        os.makedirs(out_dir, exist_ok=True)
        write_text(out_path, ENTRY + "\n")
    except OSError:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "entry.txt")
        write_text(out_path, ENTRY + "\n")

    # Read-back verification: the file on disk must hash to the digest of
    # the intended bytes; a mismatch means the write did not land intact.
    with open(out_path, "rb") as f:
        landed = f.read()
    expected = hashlib.sha256((ENTRY + "\n").encode("utf-8")).hexdigest()
    if hashlib.sha256(landed).hexdigest() != expected:
        raise SystemExit("read-back verification failed: entry.txt digest mismatch")

    ok, report = check_gate(ENTRY)
    report_path = os.path.join(out_dir, "gate-report.txt")
    write_text(
        report_path,
        json.dumps(report, indent=2, sort_keys=True) + "\n",
    )

    print(f"entry: {ENTRY}")
    print(f"chars: {report['chars']}  bytes: {report['bytes']}")
    print(f"gate valid: {ok}")
    print(f"wrote: {out_path}")
    print(f"wrote: {report_path}")
    print(f"sha256: {report['sha256']}")
    if not ok:
        print("GATE FAILED", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
