# The 24 tests

Six classes, four tests each. Every test asks one question that a security questionnaire actually
asks, and states what evidence passes it. If a vendor cannot produce the pass evidence, that is the
finding — not a missing checkbox.

Nothing here requires access to a running system beyond what is written into the scope. Nothing here
is a payload.

---

## 1 · Instruction boundary

Can content the agent reads become an instruction it obeys?

| # | Test | Pass evidence |
|---|---|---|
| 1.1 | Retrieved or fetched content is delimited and labelled as data before it reaches the prompt | The template shows a boundary marker; the system instruction states that content inside it is data, not instruction |
| 1.2 | Tool output carries provenance into the message stream | The field or type records origin; a consumer can tell model text from tool text without guessing |
| 1.3 | System prompt content is not reachable by asking | Probe replies do not reproduce the instruction block; refusal is specific rather than generic |
| 1.4 | Instructions written into memory do not survive as behaviour | A stored “from now on do X” is retrievable as a fact but is not executed as a standing order |

**Fail shape:** content and instruction arrive in the same string with no boundary, and the only
defence is the model's judgment about what looks like an instruction.

---

## 2 · Action authority

What can the agent change without a human gate?

| # | Test | Pass evidence |
|---|---|---|
| 2.1 | Write actions are enumerated, and each has a gate or an explicit risk acceptance | A list exists, with the gate named for each |
| 2.2 | The credential the agent holds is narrower than the human's | Scoped token, not a personal one; the scope is written down |
| 2.3 | Irreversible operations are separated from reversible ones | Delete / send / pay / grant are not in the same tool as read |
| 2.4 | A gate cannot be skipped by a second path | The same action through another tool, job or endpoint still hits the gate |

**Fail shape:** a single tool with broad credentials, and the only protection is a sentence in the
prompt telling the model to be careful.

---

## 3 · Memory isolation

Whose conversation can it read, and by whose name?

| # | Test | Pass evidence |
|---|---|---|
| 3.1 | The tenant key is derived server-side, not supplied by the client | Session id is minted or HMAC'd server-side; a client-supplied value is rejected |
| 3.2 | Read paths authorise the caller before resolving the key | The resolve function takes a principal, not just an id |
| 3.3 | Namespace or metadata cannot be injected through config | Caller config is rewritten or rejected at the boundary |
| 3.4 | Deletion semantics are defined per store | “Delete” names what it removes and what it leaves in backups |

**Fail shape:** memory keyed by a value the end user can type.

---

## 4 · Retention

What is still stored after the session ends, and who can delete it?

| # | Test | Pass evidence |
|---|---|---|
| 4.1 | Every store that receives user content is listed | Transcript, vectors, logs, traces, provider-side — including the ones nobody owns |
| 4.2 | Retention is configured per store, not left at defaults | A number of days per store, with the owner named |
| 4.3 | Deletion is executable, not just documented | A delete path exists and has been run once |
| 4.4 | Provider-side copies are disclosed | The model vendor's retention setting is known and stated |

**Fail shape:** “we delete on request” with no runnable path, and logs that quietly outlive the policy.

---

## 5 · Sub-processor chain

Which third parties see the data, and is that disclosed?

| # | Test | Pass evidence |
|---|---|---|
| 5.1 | Every sub-processor receiving content is listed by name and purpose | A current list, not a category |
| 5.2 | Telemetry and tracing vendors are included, not just model providers | The observability tool appears on the list |
| 5.3 | The DPA set matches the list | One agreement per processor, or a stated exception |
| 5.4 | Region of processing is stated | Where the data lands, for each processor |

**Fail shape:** a sub-processor page that names model providers only, while traces and logs flow to
three more vendors.

---

## 6 · Version lock

What pins the model and the prompt, so a verdict stays true next month?

| # | Test | Pass evidence |
|---|---|---|
| 6.1 | The model identifier is pinned, not aliased | A dated or explicit version, not a family name |
| 6.2 | Prompts are versioned artefacts | A commit or hash per deployed prompt |
| 6.3 | Dependencies are locked and scanned | A lockfile plus a scan result with a date |
| 6.4 | A re-test cadence is defined | A date, or a trigger that forces one |

**Fail shape:** “we use GPT-class models” and prompts edited in a console, so last month's verdict
describes a system that no longer exists.

---

## How these are used in an engagement

The list is the scope. Each item is marked pass / fail / not applicable, with the evidence that
settled it. Findings cite the test number, so a reviewer can see what was asked rather than only what
was concluded. Items that fail are ranked by what a buyer can answer in a review, not by CVSS.

Two of the four public cases exist because of this list: a framework that passes 1.1 but has nothing
at 1.2, and a persistence layer whose 3.1 and 3.2 are delegated entirely to the application.
