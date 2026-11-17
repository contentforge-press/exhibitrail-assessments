#!/usr/bin/env python3
"""Assessment pipeline: repository -> candidate findings -> findings.json -> PDF

Four rules, deliberately not configurable:

  1. A scanner produces candidates, never grades. Every item carries status=needs-triage
     and level="Untriaged". The scanner's own severity is reported as an observation:
     "that is a pattern, not a verdict".
  2. The same rule fired in many files is ONE item with a hit count, not many items.
     173 asserts in one tree are one class of noise, not 173 problems.
  3. A false positive must have somewhere to be written down: status=withdrawn + reason.
  4. No reusable payloads are ever produced.

Usage:
  python3 run_assessment.py --repo <dir> --client "Name" --scope "..." --out findings.json
  python3 run_assessment.py --repo <dir> --client "Name" --out findings.json --pdf report.pdf
      (--pdf requires a report builder in your own tree; the JSON is the contract.)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta


def sh(cmd, cwd=None, timeout=900):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def bandit(repo):
    rc, out, err = sh(["bandit", "-r", repo, "-f", "json", "-q"])
    try:
        data = json.loads(out)
    except Exception:
        return []
    return data.get("results", [])


# Noise classes: high hit rate, almost never a security problem in themselves.
# They are still recorded (into the CSV) but may not lead the body — the ordering
# of a report is itself an editorial claim.
NOISE = {
    "B101",   # assert
    "B110",   # try/except/pass
    "B105",   # hardcoded password string (usually a fixture)
    "B404", "B603", "B607",  # subprocess
    "B311",   # random
    "B108",   # hardcoded tmp dir
}

LEVEL = {"HIGH": "High", "MEDIUM": "Medium", "LOW": "Low"}
ORDER = {"High": 0, "Medium": 1, "Low": 2, "Info": 3, "Untriaged": 4}


def group_bandit(results):
    buckets = defaultdict(list)
    for r in results:
        key = (r.get("test_id"), r.get("issue_text"))   # same rule across files = one item
        buckets[key].append(r)
    findings = []
    for (tid, text), hits in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        fn = hits[0].get("filename")
        sev = hits[0].get("issue_severity", "LOW").upper()
        conf = hits[0].get("issue_confidence", "LOW").upper()
        line = hits[0].get("line_number")
        files_hit = sorted({os.path.basename(h.get("filename", "")) for h in hits})
        findings.append({
            "id": f"B-{tid}-{len(findings)+1}",
            "title": f"{tid}: {text[:110]}",
            "level": "Untriaged",
            "status": "needs-triage",
            "observed": (
                f"{len(hits)} occurrence(s) across {len(files_hit)} file(s) "
                f"({', '.join(files_hit[:3])}{'...' if len(files_hit) > 3 else ''}); first at {fn}:{line}. "
                f"Scanner says severity {sev} / confidence {conf} — that is a pattern, not a verdict."
            ),
            "consequence": "Candidate only. Level follows a human's reachability check, not the scanner.",
            "remediation": "Triage: is the flagged path reachable from untrusted input? If not, withdraw with a reason.",
            "owner": "—", "effort": "—", "questionnaire": "—",
            "evidence": f"bandit {tid}",
            "hits": len(hits),
            "rule": tid,
        })
    return findings


def semgrep(repo):
    for cfg in ("auto", "p/ci"):
        rc, out, err = sh(["semgrep", "--config", cfg, "--json", "--quiet", "--timeout", "60", repo], timeout=1800)
        try:
            data = json.loads(out)
        except Exception:
            continue
        res = data.get("results", [])
        if res or rc == 0:
            return res
    return []


def group_semgrep(results):
    buckets = defaultdict(list)
    for r in results:
        key = (r.get("check_id"),)   # same rule across files = one item
        buckets[key].append(r)
    out = []
    for (cid,), hits in buckets.items():
        path = hits[0].get("path")
        sev = (hits[0].get("extra", {}).get("severity") or "warning").upper()
        out.append({
            "id": f"S-{len(out)+1}",
            "title": f"{cid.split('.')[-1]}: {hits[0].get('extra', {}).get('message', '')[:100]}",
            "level": "Untriaged",
            "status": "needs-triage",
            "observed": (
                f"{len(hits)} occurrence(s) at {len({h.get('path') for h in hits})} file(s), "
                f"first {path}:{hits[0].get('start', {}).get('line')}. Scanner says {sev} — pattern only, not a verdict."
            ),
            "consequence": "Pattern match only. Confirm the data flow before grading.",
            "remediation": "Triage the source-to-sink path; withdraw if the input is not attacker-controlled.",
            "owner": "—", "effort": "—", "questionnaire": "—",
            "evidence": f"semgrep {cid.split('.')[-1]}",
            "hits": len(hits), "rule": cid,
        })
    return out


def pipaudit(repo):
    reqs = [os.path.join(repo, f) for f in ("requirements.txt", "requirements-dev.txt") if os.path.exists(os.path.join(repo, f))]
    if not reqs:
        return []
    rc, out, err = sh(["pip-audit", "-r", reqs[0], "-f", "json"], timeout=600)
    try:
        data = json.loads(out)
    except Exception:
        return []
    vulns = data.get("vulnerabilities") or data.get("dependencies") or []
    out2 = []
    for v in vulns:
        if not v.get("vulns") and not v.get("id"):
            continue
        ids = [x.get("id") for x in v.get("vulns", [])] or [v.get("id")]
        out2.append({
            "id": f"D-{len(out2)+1}",
            "title": f"{v.get('name')} {v.get('version', '')} — {', '.join([i for i in ids if i][:3])}",
            "level": "Untriaged",
            "status": "needs-triage",
            "observed": "Dependency advisory matched by pip-audit against the pinned file.",
            "consequence": "Reachability unknown: the vulnerable function may never be called.",
            "remediation": "Check whether the affected function is on a live path, then upgrade or pin.",
            "owner": "—", "effort": "—", "questionnaire": "CAIQ: supply chain",
            "evidence": "pip-audit", "hits": 1, "rule": "pip-audit",
        })
    return out2


def count_surface(root):
    files = 0
    lines = 0
    for dirpath, _, fs in os.walk(root):
        if ".git" in dirpath:
            continue
        for f in fs:
            if f.endswith((".py", ".ts", ".js", ".go", ".rb", ".java")):
                files += 1
                try:
                    with open(os.path.join(dirpath, f), "rb") as fh:
                        lines += sum(1 for _ in fh)
                except Exception:
                    pass
    return files, lines


def build_payload(args, findings, files, lines):
    signal = [f for f in findings if f.get("rule") not in NOISE]
    noise = [f for f in findings if f.get("rule") in NOISE]
    ranked = sorted(signal, key=lambda f: (ORDER.get(f["level"], 9), -int(f.get("hits", 1))))
    body, rest = ranked[:args.max], ranked[args.max:]
    rest = rest + noise
    return body, rest, noise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--scope", default="Source review of the repository named above; no deployed system, no customer data.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pdf", default=None)
    ap.add_argument("--days", type=int, default=5)
    ap.add_argument("--count-from", default=None, help="subdir used for the file/line counts (the reviewed surface)")
    ap.add_argument("--max", type=int, default=12, help="max findings in the body; the rest become an appendix index")
    ap.add_argument("--surface-label", default=None)
    a = ap.parse_args()

    findings = group_bandit(bandit(a.repo)) + group_semgrep(semgrep(a.repo)) + pipaudit(a.repo)

    counted_root = os.path.join(a.repo, a.count_from) if a.count_from else a.repo
    files, lines = count_surface(counted_root)

    body, rest, noise = build_payload(a, findings, files, lines)

    if rest:
        idx = os.path.splitext(a.out)[0] + ".candidates.csv"
        with open(idx, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["id", "level", "hits", "rule", "title"])
            for f in rest:
                w.writerow([f["id"], f["level"], f.get("hits", 1), f.get("rule", ""), f["title"]])
        print(f"appendix index: {len(rest)} candidates -> {idx}")

    if noise:
        print(f"noise classes excluded from the body: {len(noise)} ("
              f"{', '.join(sorted({f['rule'] for f in noise}))})")

    payload = {
        "client": a.client,
        "engagement": "Triage worklist — internal, not a client deliverable",
        "scope": a.scope,
        "window": f"{date.today()} to {date.today() + timedelta(days=a.days)}",
        "issued": str(date.today() + timedelta(days=a.days)),
        "surface": {"files": files, "lines": lines, "label": a.surface_label or a.count_from or "whole clone"},
        "findings": body,
        "appendix_candidates": len(rest),
        "noise_classes": sorted({f["rule"] for f in noise}),
        "note": ("WORKLIST. Every item is a candidate until triaged; nothing here is a client-facing verdict. "
                 "Some candidates will be withdrawn, and the withdrawals belong in the report."),
    }

    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"files={files} lines={lines} candidates={len(findings)} "
          f"body={len(body)} appendix={len(rest)} -> {a.out}")

    if a.pdf:
        rc, out, err = sh([sys.executable, "report/build_voice_report.py", a.out, a.pdf], cwd=os.getcwd())
        print("pdf" if rc == 0 else f"pdf failed: {err[:300]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
