# Answering the AI security questionnaire

Ten questions appear in almost every enterprise review of an AI vendor. Most vendors answer them with
adjectives. This is what a buyer actually accepts, and what to attach.

The rule underneath all ten: **an answer is only an answer if you can hand over the artefact.** If you
cannot, say so — a written "we have not implemented this" is survivable; a confident sentence that
collapses under one follow-up is not.

---

## 1. "What can the agent do without a human?"

**Weak:** "It only does what it's told."
**Survives:** an enumerated list of write actions, with the gate named per action, and the credential
scope the agent holds.

Attach: the list itself, the token scope, and one screenshot of the approval step. If a single tool
holds a broad credential, say so and state what you are doing about it — a reviewer who finds it
later costs you more than the admission does.

## 2. "Where does conversation data live, and for how long?"

**Weak:** "We take privacy seriously."
**Survives:** a table — store, what lands in it, retention period, who owns deletion. Transcript,
vector index, application logs, trace/observability vendor, and the model provider's own retention
setting.

Attach: the table, and the settings page. The store nobody owns is the one that fails review.

## 3. "How is memory separated between customers?"

**Weak:** "Each customer has their own session."
**Survives:** the tenant key is derived server-side and is not a value the client can choose; read
paths authorise the caller before resolving the key.

Attach: the function that mints the session id, and the resolve path. If your memory is keyed by a
client-supplied id — which is the default in several popular frameworks — that is a findable gap, and
the reviewer will find it.

## 4. "Which third parties see our data?"

**Weak:** a category list ("model providers, infrastructure").
**Survives:** names, purpose, region, and whether a DPA exists for each — including the observability
and eval vendors, which are usually missing from the page.

Attach: the sub-processor list, current as of a date.

## 5. "How do you stop indirect prompt injection?"

**Weak:** "We have guardrails." or "We use a classifier."
**Survives:** content is delimited and labelled as data at the prompt layer; tool output carries
provenance into the message stream; and the guardrail **fails closed** — if the classifier errors,
the request is denied, not allowed.

Attach: the prompt template boundary, the message type, and the guardrail's error path. Fail-open is
the default in a surprising amount of shipped code, and it is the first thing a reviewer tests.

## 6. "What happens when your model provider changes the model?"

**Weak:** "We use a leading model."
**Survives:** the model identifier is pinned; prompts are versioned artefacts; and there is a dated
re-test after each pinned upgrade.

Attach: the pinned identifier, the prompt hash per deployment, and the date of the last regression run.

## 7. "Who can read transcripts?"

**Weak:** "Only authorised staff."
**Survives:** the role that can read them, whether that access is logged, and whether support can read
without a customer-approved break-glass step.

Attach: the role definition and one audit log line showing a read.

## 8. "How do you delete data, and how fast?"

**Weak:** "On request."
**Survives:** a delete path that has been run at least once, propagation to vectors and summaries, a
receipt with a timestamp, and the honest caveat about backups.

Attach: the deletion receipt from a test tenant.

## 9. "Do you have SOC 2 / ISO 27001?"

**Weak:** "We're working towards it." (or worse, implying you have it)
**Survives:** the report type, the audit window, and — if none — what you have instead, stated plainly.

Attach: the report, or a one-page description of controls with owners. **Never** say you have a report
you do not have. This question is asked precisely because vendors lie here.

## 10. "What did your last penetration test cover?"

**Weak:** "We do regular testing."
**Survives:** the scope in one sentence — which surfaces, which accounts, which window — and what was
out of scope, on purpose.

Attach: the scope page, not the report. A reviewer wants to know the boundary, because the boundary is
where their own system differs from yours.

---

## Why these ten

They are not compliance questions. Each one asks the same underlying thing: **is there a control, or
only a sentence?** A vendor who can answer eight of ten with an artefact is in better shape than one
who answers ten with prose, because the reviewer's next move is to ask for the artefact anyway.

If you want to know which ones you can actually answer today, tick them against
[the 24 tests](../tests/24-tests.md) — every one of these ten maps onto a test in one of the six classes.

---

*Written by Exhibitrail — AI security assessment. Public assessments, the 24 tests, and the pipeline
that produces a worklist are all in this repository. Contact: contentforge.press@outlook.com — writing
only, no calls at any stage.*
