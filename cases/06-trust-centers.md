# 06 · What 101 AI trust centers answer — and the two questions they almost never do

**Target:** 106 trust / compliance pages published by companies in our addressable set
**Readable:** 101 of 106 (5 were gated or unreachable)
**Published:** 2026-11-17 · **Commissioned?** No
**Result:** compliance questions are answered at 44–76%. The two questions that decide an *agent*
review are answered at **5% and 7%**.

---

## Why this exists

A trust center is a company answering, in public, the questions its buyers asked. That makes it a
better dataset than a survey: nobody wrote these pages to be measured, and each page exists because
a real security review demanded it.

If you are buying an AI agent, the question is not "do they have a trust center" — most do. It is
"does the trust center answer the thing I am actually afraid of".

## Method, stated so it can be argued with

For each company we took the first trust/compliance URL we could find (paths `/trust`, `/security`,
`/compliance`, or a `trust.` subdomain) and fetched the page. We then asked one question per topic:
**does this string appear anywhere on the page.** Lowercase, no context, no reading.

That is crude on purpose. It cannot tell whether a mention is an answer or a disclaimer. It can only
tell you what a page does and does not bring up at all — and at this scale the pattern is the point.

```sh
python3 accounts/trust_center_audit.py   # reproducibility is the argument
```

## What the 101 pages cover

| Topic | Pages mentioning it | Share |
|---|---|---|
| SOC 2 / ISO 27001 | 77 | 76% |
| Data retention / deletion | 70 | 69% |
| Training on customer data | 55 | 54% |
| Penetration test | 49 | 49% |
| Subprocessor list | 44 | 44% |
| Model / AI provider named | 25 | 25% |
| **Prompt injection** | **5** | **5%** |
| **Agent tool authority** | **7** | **7%** |

## The shape of the gap

The top five topics are the vocabulary of a *compliance* review: certificates, retention, training,
pentests, vendors. A company that has been through one enterprise deal learns this list, and can
answer it.

The bottom two are the vocabulary of an *agent* review: can content the agent reads become an
instruction it obeys, and what can it change without a human gate. These are not certificate
questions. No auditor asks them, so no trust center answers them — 5% and 7% is not negligence,
it is the shape of the questionnaires the market currently sends.

Which produces a specific and slightly uncomfortable conclusion: **the documents buyers rely on
are silent on exactly the two properties that make an agent different from a web app.**

## What a buyer should do with this

Ask two questions the trust center does not answer, and accept "we will check" as an answer:

1. If a page the agent retrieves contains instructions, what makes it data rather than a command —
   and where is that enforced: template, prompt, or permission?
2. What can the agent change without a human approving it, and is that list written down anywhere a
   customer can read?

A vendor that answers these two has done work that no certificate covers. A vendor that has not
thought about them will say something about guardrails.

## What a vendor should do with this

Not "add a page". A page that says "we mitigate prompt injection" is the least useful possible
response — it is an adjective. The useful artefact is smaller and harder: one page per agent
surface, stating what the boundary is, where it is implemented, and what test would show it holds.

That artefact is what our 24 tests ask for, and it is why the tests are public.

## Limits

- Keyword presence is not comprehension: 5% may undercount pages that address the risk in other
  words ("untrusted content", "instruction hierarchy"). We did not search synonyms, and say so.
- The set is our addressable list, not the market. It skews toward AI-native companies that have
  been through at least one enterprise deal.
- Five pages were unreachable and are excluded from the denominator.
- A page that mentions a topic may do so in a way that fails the test. This counts vocabulary, not
  quality.

*Written by Exhibitrail. Five other assessments, the 24 tests and the pipeline are in this
repository. Evidence, not adjectives.*
