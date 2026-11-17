#!/usr/bin/env python3
"""Suggest withdrawals from the library. Never decide them.

A warning that is deliberately in the code: every `when` clause in the library is a human judgement.
The script can read a rule id and a filename; it cannot read whether a string is a live credential.
So it writes status=suggested-withdraw by default, and only `--confirm` turns a suggestion into a
withdrawal. A batch withdrawal without that flag would be passing a human judgement off as a machine one.

Usage:
  python3 triage.py lookup B106                  # read the conditions for one rule
  python3 triage.py apply f.json --out t.json     # fill reasons as SUGGESTIONS
  python3 triage.py apply f.json --confirm        # a human accepts them
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


def cmd_lookup(rule):
    e = load().get(rule)
    if not e:
        print(f"not in the library: {rule}. This one must be judged by a person and written from scratch.")
        return 1
    print(f"rule: {rule}\nwhen: {e['when']}\nreason: {e['reason_en']}\nwhat would change it: {e['what_would_change_it']}")
    return 0


def match(rule, lib):
    """Semgrep check ids are dotted; the library uses short names. Match by segment."""
    if rule in lib:
        return rule
    for seg in str(rule).split("."):
        if seg in lib:
            return seg
    return None


def cmd_apply(src, out, dry, confirm=False):
    lib = load()
    d = json.load(open(src, encoding="utf-8"))
    hit = 0
    for f in d.get("findings", []):
        rule = match(f.get("rule", ""), lib)
        if rule and str(f.get("status", "")) != "withdrawn":
            hit += 1
            if not dry:
                f["status"] = "withdrawn" if confirm else "suggested-withdraw"
                f["level"] = "Low"
                f["reason"] = lib[rule]["reason_en"]
                f["consequence"] = "Withdrawn after triage. " + lib[rule]["reason_en"]
                f["remediation"] = "No action required. Recorded so the test log shows what was examined."
                f["_suggested_by"] = rule
    if dry:
        print(f"{hit} item(s) match a library rule (suggested). Others need a person. Add --confirm to write withdrawn.")
        return 0
    Path(out).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    left = [f for f in d["findings"] if f.get("status") != "withdrawn"]
    verb = "withdrawn" if confirm else "suggested (needs a human)"
    print(f"{verb}: {hit}; still needing a person: {len(left)} -> {out}")
    for f in left:
        print("  pending:", f.get("id"), f.get("rule"))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["lookup", "apply"])
    ap.add_argument("target")
    ap.add_argument("--out", default="triaged.json")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    if a.cmd == "lookup":
        sys.exit(cmd_lookup(a.target))
    sys.exit(cmd_apply(a.target, a.out, a.dry, a.confirm))
