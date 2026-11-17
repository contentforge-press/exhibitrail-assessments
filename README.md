# AI security assessments, published in full

Four source reviews of public repositories. Each is reproducible, uncommissioned, and written so a
security reviewer can check the claim rather than trust the prose. No payloads are published; no
client data appears anywhere.

**What these are.** An agent is not a web app with a model bolted on. It takes actions, keeps
memory, calls tools, and passes text it did not write into places it did not choose. The interesting
failures live at those seams, and scanners do not see them: a static analyzer reads the code, not
the trust boundary.

**What these are not.** A certification. A statement on behalf of any maintainer. A CVSS score.
Severity here reflects *what a buyer can answer in a security review*, not what a scanner can flag.

---

## [The 24 tests](tests/24-tests.md), published in full

Six classes, four tests each, with the evidence that passes each one. It is the scope we work to —
published so you can read the questions before you decide anything.

## The six classes we test

1. **Instruction boundary** — can content the agent reads become an instruction it obeys?
2. **Action authority** — what can it change without a human gate?
3. **Memory isolation** — whose conversation can it read, and by whose name?
4. **Retention** — what is still stored after the session ends, and who can delete it?
5. **Sub-processor chain** — which third parties see the data, and is that disclosed?
6. **Version lock** — what pins the model and the prompt so a verdict stays true next month?

---

## The four files

| # | Target | Surface | Result |
|---|---|---|---|
| [1](cases/01-voice-agent-framework.md) | livekit/agents · 86,760 lines, 237 files | voice agent framework | **174 Bandit hits → 1 real** + 2 classes of false positive |
| [2](cases/02-retrieval-app.md) | langchain-ai/chat-langchain · 3,455 lines | retrieval / RAG app | **11 findings, 2 High**, 62/100 |
| [3](cases/03-llm-gateway.md) | litellm · 28,903 lines (proxy auth) | LLM gateway | one decision made on **two paths**, one hardened |
| [4](cases/04-agent-memory.md) | langgraph · 29,082 lines (core + savers) | persistence | **design observation**, severity depends on the app |

Every file states its own limits. Where something looked like a finding and was not, the file says
so and gives the reason — that is the part reviewers actually use.

---

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
