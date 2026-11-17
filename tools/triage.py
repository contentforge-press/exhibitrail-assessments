#!/usr/bin/env python3
"""Suggest withdrawals from the library. Never decide them.

A warning that is deliberately in the code: every `when` clause in the library is a human judgement.
The script can read a rule id and a filename; it cannot read whether a string is a live credential.
So it writes status=suggested-withdraw by default, and only `--confirm` turns a suggestion into a
withdrawal. A batch withdrawal without that flag would be passing a human judgement off as a machine one.

Usage:
  python3 triage.py lookup B106
  python3 triage.py apply findings.json --out triaged.json           # suggestions only
  python3 triage.py apply findings.json --out triaged.json --confirm # a human accepts them
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: pip install pyyaml")

LIB = Path(__file__).with_name("withdraw_library.yaml")


def load():
    return {e["rule"]: e for e in yaml.safe_load(LIB.read_text(encoding="utf-8"))}


def match(rule, lib):
    """Semgrep check ids are dotted; the library uses short names. Match by segment."""
    if rule in lib:
        return rule
    for seg in str(rule).split("."):
        if seg in lib:
            return seg
    return None


def cmd_lookup(rule):
    e = load().get(rule)
    if not e:
        print(f"not in the library: {rule}. This one has to be judged by a person and written from scratch.")
        return 1
    print(f"rule: {rule}\nwhen: {e['when']}\nreason: {e['reason_en']}\nwhat would change it: {e['what_would_change_it']}")
    return 0


def cmd_apply(src, out, dry, confirm):
    lib = load()
    d = json.load(open(src, encoding="utf-8"))
    hit = 0
    for f in d.get("findings", []):
        rule = match(f.get("rule", ""), lib)
        if rule and str(f.get("status", "")) != "withdrawn":
            hit += 1
            if not dry:
                f["status"] = "withdrawn" if confirm else "suggested-withdraw"
                f["reason"] = lib[rule]["reason_en"]
                f["consequence"] = "Withdrawn after triage. " + lib[rule]["reason_en"]
                f["remediation"] = "No action required. Recorded so the test log shows what was examined."
                f["_suggested_by"] = rule
    if dry:
        print(f"{hit} item(s) match a library rule (suggested). Add --confirm to write withdrawn.")
        return 0
    Path(out).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    left = [f for f in d["findings"] if f.get("status") != "withdrawn"]
    verb = "withdrawn" if confirm else "suggested (needs a person)"
    print(f"{verb}: {hit}; still needing a person: {len(left)} -> {out}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    lk = sub.add_parser("lookup", help="read the conditions for one rule")
    lk.add_argument("rule")
    ap2 = sub.add_parser("apply", help="fill reasons into a findings file")
    ap2.add_argument("src")
    ap2.add_argument("--out", default="triaged.json")
    ap2.add_argument("--dry", action="store_true")
    ap2.add_argument("--confirm", action="store_true", help="a human accepts the suggestions")
    a = ap.parse_args()
    if a.cmd == "lookup":
        return cmd_lookup(a.rule)
    return cmd_apply(a.src, a.out, a.dry, a.confirm)


if __name__ == "__main__":
    sys.exit(main())
