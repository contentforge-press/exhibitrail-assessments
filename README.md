# AI security assessments, published in full

Four source reviews of public repositories, plus one coverage count — five assessments in total.
Each is reproducible, uncommissioned, and written so a security reviewer can check the claim
rather than trust the prose. No payloads are published; no client data appears anywhere.

**What these are.** An agent is not a web app with a model bolted on. It takes actions, keeps
memory, calls tools, and passes text it did not write into places it did not choose. The interesting
failures live at those seams, and scanners do not see them: a static analyzer reads the code, not
the trust boundary.

**What these are not.** A certification. A statement on behalf of any maintainer. A CVSS score.
Severity here reflects *what a buyer can answer in a security review*, not what a scanner can flag.

---

## The five files

| # | Target | Surface | Result |
|---|---|---|---|
| [1](cases/01-voice-agent-framework.md) | livekit/agents · 86,760 lines, 237 files | voice agent framework | **174 Bandit hits → 1 real** + 2 classes of false positive |
| [2](cases/02-retrieval-app.md) | langchain-ai/chat-langchain · 3,455 lines | retrieval / RAG app | **11 findings, 2 High**, 62/100 |
| [3](cases/03-llm-gateway.md) | litellm · 28,903 lines (proxy auth) | LLM gateway | one decision made on **two paths**, one hardened |
| [4](cases/04-agent-memory.md) | langgraph · 29,082 lines (core + savers) | persistence | **design observation**, severity depends on the app |
| [5](cases/05-telnyx-examples.md) | team-telnyx/telnyx-code-examples · 293 Python samples | sample coverage | **181 of 293 verify a webhook** (62%) — and the direction they do not cover |

Every file states its own limits. Where something looked like a finding and was not, the file says
so and gives the reason — that is the part reviewers actually use.
