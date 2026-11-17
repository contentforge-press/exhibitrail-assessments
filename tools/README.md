# The pipeline behind the reports

`run_assessment.py` is the tool that turns a repository into a **worklist**: `bandit` + `semgrep` +
`pip-audit`, merged, de-noised, and emitted as JSON. A human then does the only part that matters —
turning `Untriaged` into `High` or `withdrawn`, with a reason.

```bash
pip install bandit semgrep pip-audit
python3 run_assessment.py --repo /path/to/repo --count-from src \
  --client "Acme agent" --out findings.json
```

## The four rules, and why they exist

**1. A scanner produces candidates, never grades.**
The first run of this tool printed `12 High` at the top of a report. That was the tool lying: a
scanner's `ERROR` is a pattern match, not a verdict. Every item now carries `level="Untriaged"` and
the scanner's opinion is demoted to a sentence inside the finding:

> *Scanner says severity LOW / confidence HIGH — that is a pattern, not a verdict.*

**2. The same rule in many files is one item.**
13,499 `assert` hits across 342 files are one class of noise, not 13,499 problems. Merging by rule
took a 586-item dump down to 99 items — and a 113-page report down to seven.

**3. Noise classes do not lead the body.**
`B101 B105 B108 B110 B311 B404 B603 B607` are recorded in the CSV and kept out of the verdict page.
The ordering of a report is an editorial claim, so the noise is not allowed to make it.

**4. The body has a cap (default 12).**
Everything else goes to `*.candidates.csv`. A report nobody finishes is not a deliverable; length is
part of the product.

## Output

| file | what it is |
|---|---|
| `findings.json` | the worklist: `surface` (files / lines / label), `findings`, `appendix_candidates`, `noise_classes` |
| `*.candidates.csv` | every candidate kept out of the body |
| `*.pdf` | optional; needs a report builder in your own tree — the JSON is the contract |

## What it deliberately does not do

No exploitation, no payloads, no traffic to a deployed system. It reads source. The interesting
failures in an agent — an instruction that arrives inside retrieved content, a tool output with no
provenance, a tenant key the tenant controls — are **not visible to this tool**. That is the whole
argument for a human review, and it is why the [24 tests](../tests/24-tests.md) exist.
