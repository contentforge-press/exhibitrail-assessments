# 07 · openai/openai-agents-python — a clean result, and three seams

**Target** `openai/openai-agents-python` at commit `9e05bd5bf299a5ddbb25f7fec8da10bf2baf6133` (2026-11-17).
**Scope** `src/` only: 317 Python files, 134,657 lines.
**Method** Bandit 1.9.4 (JSON, default rules) + a read of the tool-call lifecycle. No dynamic execution, no fuzzing,
no payloads. Nothing was sent to the maintainers before publication; this is not a disclosure channel.

---

## What the scan produced

| Severity | Count | Triage |
|---|---|---|
| HIGH | 1 | **not exploitable** — SHA-1 used to shorten MCP tool names (`src/agents/mcp/util.py:439`), a collision-resistance-free namespace suffix, not a security primitive |
| MEDIUM | 74 | mostly `B608` hardcoded SQL strings in test fixtures (40) and `B604` function calls with `shell=True` in example helpers (18); read individually, none on a path a model can reach |
| LOW | 235 | `assert`-based narrowing and `try/except/pass` — noise, kept in the count so the ratio is honest |

**310 hits, 0 real.** That is the result this time. Publishing it matters because a practice that only ever
finds something is a practice you cannot use to decide anything: if every review ends in "critical", the word
stops meaning anything.

---

## Three seams worth a buyer's attention

### O-1 · Tool output arrives without provenance

`ToolCallOutputItem` carries `raw_item` (a string form of the output) and `output` (whatever the tool returned).
When the tool result re-enters the model's context it is a plain `function_call_output` — the same shape as any
other text the model is asked to read. There is no marker saying *this text came from a tool that read a
document a stranger wrote*.

Consequence, stated plainly: an SDK built on this cannot, by itself, tell the model which parts of its context are
data and which are instructions. Anything that watches for injected instructions has to be added by the
application, above the SDK. This is a design note, not a bug — but it is the row most trust centres omit, and the
row our 101-vendor count found on 7% of pages.

### O-2 · Approvals are per call, with a legacy path that rebuilds missing bindings

`needs_approval` can be a bool or a function of `(run_context, action, call_id)`, and approval is keyed to the
call id. When a run is serialized and resumed, `RunContextWrapper` can reconstruct an approval binding that was
not persisted — gated by `_allow_legacy_approval_binding_reconstruction`
(`src/agents/run_context.py:201`, used at `agent.py:855`).

We are **not** claiming that an approval for call A can authorize call B. We are saying the fallback exists,
that it is opt-in, and that proving either way needs a run we did not perform. Marked **Untriaged** on purpose:
"we could not rule it out without executing" is a different sentence from "it is safe".

### O-3 · A hosted shell tool refuses to be approval-gated

`ShellTool.__post_init__` raises `UserError` when `environment` is hosted and `needs_approval` is not False
(`src/agents/tool.py:1533-1541`). The error is explicit, which is the right choice — a silent downgrade would be
worse. But it means the answer to "can shell commands require human approval?" is **yes in local mode, no in
hosted mode**, and a buyer who reads only the docstring for `needs_approval` will answer that question wrongly.

---

## What this review cannot support

- **No dynamic testing.** Approval bypasses, sandbox escapes and MCP server trust were not exercised.
- **`src/` only.** Tests, examples and docs were counted, not read.
- **Bandit is not a taint tracker.** It sees calls, not flows; the SQL and `shell=True` hits are noise because
  nothing model-controlled reaches them, and we assert that from reading, not from a tool.
- **One commit.** The judgement holds for `9e05bd5` and not for the project.
- **No disclosure.** Nothing was reported privately first; nothing here is a vulnerability report.

---

## Why publish a clean one

A buyer choosing between two vendors gets no information from two reviews that both say "critical". A practice
that prints the same verdict on a well-kept codebase as on a neglected one is a pricing exercise, not a
measurement. This is the case where the measurement came back quiet — recorded so the next loud one can be
believed.

Reproduce: `git clone --depth 1 https://github.com/openai/openai-agents-python && bandit -r src -f json`.
