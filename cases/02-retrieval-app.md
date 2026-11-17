# Case 2 — a retrieval app, two Highs

**Target:** `langchain-ai/chat-langchain` · 24 files · 3,455 lines.
**Method:** Bandit + Semgrep + `pip-audit` + a manual read of the retrieval and tool paths.

## Result

11 findings — 2 High, 5 Medium, 2 Low, 2 Informational. Composite **62/100 (C)**.

### H-1 — no trust boundary between tool output and instructions

Content returned by the retrieval tool is concatenated into the prompt with no delimiter, no
provenance, and no instruction to treat it as data. A document in the index can therefore address
the model directly. This is the textbook indirect-injection shape, and it is the finding most likely
to be exploitable in production because the corpus is often user-supplied.

### H-2 — a guardrail classifier fails open

The guardrails check returns "allowed" when the classifier itself errors. A dependency outage or a
timeout therefore disables the control instead of denying the request. Fail-open is a policy
decision that should be made explicitly and written down; here it is an implicit default.

### Positive

Outbound fetches validate the resolved address hop by hop, which is real SSRF work rather than a
regex on the URL string.

### Withdrawn

Semgrep flagged `prompt_provenance.py:91` as a credential leak. It is not: the value is a hash of
public content used for cache keys. Reported, verified, withdrawn.

## Limits

Source review of public code. No exploit payload is reproduced here.
