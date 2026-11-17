# Case 1 — a voice agent framework, 174 hits, one real

**Target:** `livekit/agents` · 237 files · 86,760 lines · cloned at depth 1, no running system touched.
**Method:** Bandit over the tree, then manual triage of every class of hit, then a read of the tool
and data paths that a scanner cannot follow.

## Result

| | |
|---|---|
| Scanner hits | 174 |
| Real findings | **1** |
| Classes of false positive | 2 (173 of the hits) |

### M-1 — tool output enters the transcript with no provenance marker

In `_proto.py`, a tool's return value is assigned straight into the message stream
(`output=item.output`). Once there, it is indistinguishable from something the model produced.
A downstream consumer that filters or grades messages by role has no way to tell "the model said
this" from "a third-party API returned this."

This is the seam where indirect prompt injection lives, and it is a *design* property, not a bug:
the framework hands the application a transcript and leaves provenance to the application. The
finding is that nothing in the type or the field names records it, so the default integration
inherits the risk silently.

### The false positives, and why they matter

- **B301 (pickle)** — the hit sits after a `socket.socketpair()` that runs before the fork. No path,
  no port, no attacker-controlled input reaches it. Reported, then withdrawn.
- **173 × B101 (assert)** — `assert` is not a security control. Flagging it is noise, and noise is
  the reason teams stop reading scanner output.

### Positive

`lk.pii.user_transcript` gives transcript data an explicit classification, so retention and redaction
can be attached to it. Few frameworks label their own data.

## Limits

Source review only. No deployed system, no traffic, no client data. The severity of M-1 depends
entirely on the application built on top of it.
