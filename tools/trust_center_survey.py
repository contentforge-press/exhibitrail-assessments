#!/usr/bin/env python3
"""Survey published trust centers: what do they actually answer?

Takes a list of domains and, for each, fetches the first trust/compliance page it can find,
then records whether one string per topic appears anywhere on the page. Binary, no context.

    python3 trust_center_survey.py --domains domains.txt --out coverage.csv

Why this is worth running: a trust center exists because a buyer asked. Pages are written for
reviewers, not for measurement, so the distribution you get is closer to what the market asks
than to what a vendor wishes it asked.

Two honesty notes baked into the output:
  - readable=0 means the page could not be fetched and is excluded from any denominator.
  - a topic recorded as 0 means "this string did not appear". It does NOT mean the control is
    missing. A page may answer in other words. Count vocabulary, not quality.
"""
import argparse, csv, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "trust-center-survey/1.0 (reproducible research; no crawling)"}
PATHS = ["/trust", "/trust-center", "/security", "/security-and-compliance", "/compliance", "/privacy"]
KEYS = ("trust center", "vanta", "drift", "safebase", "subprocessor", "soc 2", "soc2", "iso 27001", "gdpr", "dpa")

TOPICS = {
    "soc2_iso": ("soc 2", "soc2", "iso 27001", "iso/iec 27001"),
    "subprocessors": ("subprocessor", "sub-processor", "sub processor"),
    "pentest": ("penetration test", "pentest", "pen test"),
    "retention": ("retention", "retain", "deletion", "delete"),
    "model_provider": ("openai", "anthropic", "azure openai", "model provider", "llm provider"),
    "training_data": ("train", "training data", "not used to train"),
    "prompt_injection": ("prompt injection", "prompt-injection", "jailbreak"),
    "tool_authority": ("tool call", "tool-call", "function call", "agent action", "autonomous"),
}

def fetch(url, timeout=10):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
        return r.read(500_000).decode("utf-8", "replace").lower()
    except Exception:
        return ""

def page_for(domain):
    for sub in ("", "trust.", "security.", "compliance."):
        for p in (PATHS if sub == "" else ["/"]):
            html = fetch(f"https://{sub}{domain}{p}")
            if html and sum(k in html for k in KEYS) >= 2:
                return f"https://{sub}{domain}{p}", html
    return "", ""

def one(domain):
    url, html = page_for(domain)
    if not html:
        return {"domain": domain, "url": "", "readable": 0, **{t: 0 for t in TOPICS}}
    return {"domain": domain, "url": url, "readable": 1,
            **{t: int(any(s in html for s in subs)) for t, subs in TOPICS.items()}}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domains", required=True, help="one domain per line")
    ap.add_argument("--out", default="coverage.csv")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    doms = [l.strip() for l in open(a.domains, encoding="utf-8") if l.strip() and not l.startswith("#")]
    if not doms:
        print("no domains"); return 2
    rows = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        for r in ex.map(one, doms):
            rows.append(r)
            print(f"{'ok ' if r['readable'] else '-- '}{r['domain']}")
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["domain", "url", "readable", *TOPICS])
        w.writeheader(); w.writerows(rows)
    ok = [r for r in rows if r["readable"]]
    print(f"\nreadable {len(ok)} / {len(rows)}")
    for t in TOPICS:
        n = sum(r[t] for r in ok)
        print(f"  {t:18s} {n:3d} / {len(ok)}  ({(n/len(ok)*100 if ok else 0):.0f}%)")
    print(f"\u2192 {a.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
