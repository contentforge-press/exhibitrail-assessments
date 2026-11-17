# AI security assessments, published in full

Five source reviews, one coverage count, and one survey of 101 trust centers — seven assessments in
total. Each is reproducible, uncommissioned, and written so a security reviewer can check the claim
rather than trust the prose. No payloads are published; no
client data appears anywhere.

**Want a review?** Three facts on the intake page build the email for you — repository, what the
agent can do without approval, deadline. Written scope back in 24 hours, no call at any stage:
`4mg8p8hp0ddk3.doubao.link/app/app_17j74pwsvp1`

**What these are.** An agent is not a web app with a model bolted on. It takes actions, keeps
memory, calls tools, and passes text it did not write into places it did not choose. The interesting
failures live at those seams, and scanners do not see them: a static analyzer reads the code, not
the trust boundary.

**What these are not.** A certification. A statement on behalf of any maintainer. A CVSS score.
Severity here reflects *what a buyer can answer in a security review*, not what a scanner can flag.

---

## The files

| # | Target | Surface | Result |
|---|---|---|---|
| [1](cases/01-voice-agent-framework.md) | livekit/agents · 86,760 lines, 237 files | voice agent framework | **174 Bandit hits → 1 real** + 2 classes of false positive |
| [2](cases/02-retrieval-app.md) | langchain-ai/chat-langchain · 3,455 lines | retrieval / RAG app | **11 findings, 2 High**, 62/100 |
| [3](cases/03-llm-gateway.md) | litellm · 28,903 lines (proxy auth) | LLM gateway | one decision made on **two paths**, one hardened |
| [4](cases/04-agent-memory.md) | langgraph · 29,082 lines (core + savers) | persistence | **design observation**, severity depends on the app |
| [5](cases/05-telnyx-examples.md) | team-telnyx/telnyx-code-examples · 293 Python samples | sample coverage | **181 of 293 verify a webhook** (62%) — and the direction they do not cover |
| [6](cases/06-trust-centers.md) | 101 published AI trust centers | what buyers are shown | compliance answered at 44–76%; **prompt injection 5%, tool authority 7%** |
| [7](cases/07-agent-sdk.md) | openai/openai-agents-python · 134,657 lines, 317 files | agent SDK | 310 Bandit hits → **0 real**; 1 HIGH is a false positive; 3 seams noted |

## Reading guides

- [What to ask an AI vendor, and what counts as an answer](guides/what-to-ask-an-ai-vendor.md)
  ([one-page version, built to forward](https://4mg8p8hp0ddk3.doubao.link/app/app_17j77t2prc5)) —
  20 questions for the buyer's side of the table: weak answer, the answer that survives a
  follow-up, and the artefact to demand.
- [How to read a source review](guides/how-to-read-a-source-review.md) — what Untriaged and
  withdrawn mean, and what each column cannot support.
- [Answering the AI security questionnaire](guides/answering-the-ai-security-questionnaire.md) —
  10 questions a vendor gets, and what a survivable answer looks like.

Every file states its own limits. Where something looked like a finding and was not, the file says
so and gives the reason — that is the part reviewers actually use.

---

## [The 24 tests](tests/24-tests.md), published in full

Six classes, four tests each, with the evidence that passes each one. It is the scope we work to —
published so you can read the questions before you decide anything.

## [How to read a source review without being sold to](guides/how-to-read-a-source-review.md)

What `Untriaged` and `withdrawn` actually mean, what each column can and cannot support, and the
three questions worth asking any vendor — including the two absences that are deliberate (no
payloads, no grades invented from scanner levels).

## [Answering the AI security questionnaire](guides/answering-the-ai-security-questionnaire.md)

The ten questions that appear in almost every enterprise review, with the answer that survives a
follow-up and the artefact to attach — including the ones where the honest answer is "we have not
implemented this".

## The six classes we test

1. **Instruction boundary** — can content the agent reads become an instruction it obeys?
2. **Action authority** — what can it change without a human gate?
3. **Memory isolation** — whose conversation can it read, and by whose name?
4. **Retention** — what is still stored after the session ends, and who can delete it?
5. **Sub-processor chain** — which third parties see the data, and is that disclosed?
6. **Version lock** — what pins the model and the prompt so a verdict stays true next month?

---

## The pipeline behind the reports

[`tools/run_assessment.py`](tools/README.md) is published too. It merges Bandit, Semgrep and pip-audit
into a worklist and refuses to grade: every item is `Untriaged` until a human checks reachability, and
the same rule fired in 342 files is one item, not 342. The tool cannot see the failures that matter
most in an agent — that is the argument for the 24 tests above.

## How an engagement runs

Written scope with eight rules of engagement, signed before anything is touched. Nothing outside
that scope is tested. Five working days from signed scope to a verdict. Five deliverables:

- written scope and what was deliberately excluded
- the test list, with pass / fail / not-applicable per item
- findings, each with the reasoning that separates a real issue from a scanner artifact
- a one-page summary a non-technical buyer can file next to a SOC 2 report
- a re-test window

**Pricing.** Quick Scan $2,900 · Deep $6,500 · Monthly retest $2,500.

**Contact.** contentforge.press@outlook.com — writing only. No calls, no voice, at any stage.

---

*These files are source reviews of public code, performed without access to any deployed system.
They carry no warranty and no attestation.*
