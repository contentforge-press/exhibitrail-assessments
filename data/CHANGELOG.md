# Changelog — trust center coverage

## 2026-11-17 · snapshot 1 (commit 059f1e9)

- First published matrix: 106 domains, 8 topics, 101 readable.
- Coverage: SOC 2 / ISO 27001 76%, retention 69%, training data 54%, penetration test 49%,
  subprocessors 44%, model provider 25%, prompt injection 5%, agent tool authority 7%.
- Script `tools/trust_center_survey.py` published alongside, so the run can be repeated.

Known weaknesses at this snapshot, recorded so a later version can be judged against them:

- Single-string matching per topic; no synonyms. Prompt injection may be undercounted
  ("untrusted content", "instruction hierarchy").
- One page per company (the first that matched). A company with a deeper subprocessor page
  and a shallow security page is scored by whichever came first.
- Set is our addressable list, not the market: it over-represents AI-native companies that
  have been through at least one enterprise deal.
- Five domains unreadable (abridge, chatwoot, fathom.video, nank.ai, thoropass).
