# 05 · Telnyx code examples — how many samples verify a webhook before trusting it

**Target:** `team-telnyx/telnyx-code-examples` (public)
**Surface:** 293 directories containing Python
**Published:** 2026-11-17 · **Commissioned?** No
**Result:** 181 samples (62%) check a signature before trusting an event; 112 do not.
**Verdict:** the samples are better than most public sample repos. The gap is not in the samples —
it is in what the samples cannot show: the outbound direction.

---

## Why this one is different from 01–04

Cases 01–04 are source reviews: I read one system's trust boundaries and wrote down what a buyer
would ask. This case is a **coverage count**. It answers one question — do the code examples that
ship with a public platform verify events before acting — and it answers it with a number you can
reproduce in a minute.

It is published for two reasons. First, it is a useful question for anyone building on this
platform: the samples are what gets copied into production. Second, it is the smallest honest
demonstration of the difference between reading code and believing documentation.

## Method

```sh
git clone --depth 1 https://github.com/team-telnyx/telnyx-code-examples
# for each directory containing .py: does the code call a signature check before acting?
grep -rl "unwrap(" --include=*.py .
```

A sample counts as verifying if it calls the SDK's unwrap/verify path, checks an Ed25519 signature,
or otherwise validates the event before reading the payload. Filenames and README claims are
ignored; only code counts.

## What the numbers are

| Category | Samples | Verifying | Share |
|---|---|---|---|
| AI / voice / SMS product samples | 155 | 104 | 67% |
| Other (account, messaging, misc.) | 106 | 62 | 58% |
| Number / SIM provisioning | 25 | 11 | 44% |
| Demo, game, tutorial | 7 | 4 | 57% |
| **Total** | **293** | **181** | **62%** |

For comparison: in most SDK sample repositories the equivalent number is close to zero, because
sample code is written to show the happy path. 62% is not a marketing number — it is a
maintenance number, and it says someone on the team treats samples as documentation that will be
copied.

## What this count cannot tell you

- **It cannot tell you whether the deployed platform verifies events.** It counts samples.
- **It cannot tell you whether verification is enforced or optional in production.** A sample that
  calls `unwrap()` proves the SDK *can*; it does not prove the service *requires*.
- **It cannot tell you anything about the outbound direction.** This is the part that matters and
  the reason this file exists at all, below.

## The direction the samples do not cover

Every one of these samples verifies **inbound**: it receives an event and decides whether to trust
it. None of them addresses the **outbound** hop, which is where an AI assistant becomes an
initiator rather than a responder.

An assistant's webhook tool takes a URL from the tenant. So the flow is:

```
inbound event ──► verified ◄── the samples stop here
                       │
                       └──► tool call ──► HTTP request to a URL the tenant chose
                                              (made with the platform's account, not the tenant's)
```

Three questions follow, and none of them can be answered by reading samples:

1. **Is the outbound URL constrained?** An allowlist is a different product from a free-form field.
2. **Does the tool's response carry provenance into the model context?** A JSON body returned
   mid-call is text arriving from outside the system; whether the model can tell it apart from
   its own instructions determines whether that path is an instruction channel.
3. **What is the retention path for transcripts and gathered input?** The samples contain no
   `delete` call, so the question is not whether data is stored but where it stops being.

These are the questions I would ask before putting an assistant in front of a customer. They are
also the questions a buyer's security review asks, in roughly that order.

## What this file is not

Not a claim that Telnyx has a vulnerability. Not a statement on behalf of Telnyx. Not a rating.
It is a count, a method, and three questions the count cannot answer.

*Written by Exhibitrail. Four other assessments and the 24 tests are in this repository;
`tools/` reproduces the scanning pipeline. Evidence, not adjectives.*
