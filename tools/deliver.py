#!/usr/bin/env python3
"""One command for the whole delivery chain: scan -> suggest -> human confirms -> report.

Why confirmation is an argument, not a prompt:
  A delivery is signed by a person; it cannot be a script clicking "agree". --confirm must name the
  rule ids explicitly. Anything not named stays Untriaged and is still printed in the report, so
  nothing disappears quietly.

Usage:
  python3 deliver.py --repo <dir> --client "Name" --outdir out/ --confirm B101,B106,B110 \\
      [--count-from src] [--max 12] [--zh-map zh.json]

Output:
  out/worklist.json      every candidate, untouched
  out/triaged.json       after confirmation (only --confirm rules are withdrawn)
  out/report.pdf         the client-facing report
  out/internal_zh.pdf    internal bilingual copy (only with --zh-map)
  out/pending.txt        candidates nobody has judged yet — these are NOT findings
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--client", required=True)
    ap.add_argument("--outdir", default="out")
    ap.add_argument("--confirm", default="", help="rule ids, comma separated; only these may be withdrawn")
    ap.add_argument("--count-from", default=None)
    ap.add_argument("--surface-label", default=None)
    ap.add_argument("--max", type=int, default=12)
    ap.add_argument("--scope", default=None)
    ap.add_argument("--zh-map", default=None, help="bilingual summary map (optional)")
    a = ap.parse_args()

    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    work = out / "worklist.json"

    # 1) scan
    cmd = [sys.executable, str(HERE / "run_assessment.py"), "--repo", a.repo, "--client", a.client,
           "--out", str(work), "--max", str(a.max)]
    if a.count_from:
        cmd += ["--count-from", a.count_from]
    if a.surface_label:
        cmd += ["--surface-label", a.surface_label]
    if a.scope:
        cmd += ["--scope", a.scope]
    rc, so, se = run(cmd)
    print("[1/4] scan:", so.splitlines()[-1] if so else se[:200])
    if rc != 0:
        print("scan failed:", se[:400])
        return 1

    # 2) suggest withdrawals
    rc, so, se = run([sys.executable, str(HERE / "triage.py"), "apply", str(work), "--out", str(out / "suggested.json")])
    print("[2/4] suggest:", so.splitlines()[0] if so else se[:200])

    # 3) confirm only the rules a person named
    d = json.load(open(out / "suggested.json", encoding="utf-8"))
    allowed = {x.strip() for x in a.confirm.split(",") if x.strip()}
    confirmed, still = 0, []
    for f in d["findings"]:
        rule = f.get("_suggested_by") or ""
        if f.get("status") in ("suggested-withdraw", "needs-triage") and rule and rule in allowed:
            f["status"] = "withdrawn"
            confirmed += 1
        else:
            if f.get("status") in ("suggested-withdraw", "withdrawn"):
                f["status"] = "needs-triage"
            if f.get("status") != "withdrawn":
                still.append(f)
                f.setdefault("level", "Untriaged")
    d["engagement"] = "Quick Scan — source review"
    d["note"] = ("Every item with level Untriaged has NOT been judged. It is printed so the reviewer can see "
                 "what remains open; it is not a finding and must not be read as one.")
    tri = out / "triaged.json"
    json.dump(d, open(tri, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[3/4] confirmed withdrawn: {confirmed}; still unjudged: {len(still)} (see pending.txt, not findings)")

    pend = out / "pending.txt"
    pend.write_text(
        "\n".join(f"{f['id']}\t{f['level']}\t{f.get('rule', '')}\t{f['title'][:80]}" for f in still)
        + "\n\n# Unjudged. They appear as Untriaged in the report and must not be cited as findings.\n",
        encoding="utf-8",
    )

    # 4) build the report
    rep = out / "report.pdf"
    rc, so, se = run([sys.executable, str(ROOT / "report" / "build_voice_report.py"), str(tri), str(rep)])
    print("[4/4] report:", "ok" if rc == 0 else se[:300])
    if a.zh_map and (ROOT / "report" / "build_internal_zh.py").exists():
        rc2, so2, se2 = run([sys.executable, str(ROOT / "report" / "build_internal_zh.py"), str(tri), a.zh_map,
                             str(out / "internal_zh.pdf")])
        print("      internal zh copy:", "ok" if rc2 == 0 else se2[:200])

    print("\noutput:", out)
    for f in sorted(out.iterdir()):
        print(f"  {f.name}  {f.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
