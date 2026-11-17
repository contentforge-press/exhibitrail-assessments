# How to read a source review without being sold to

Most security documents are written to be agreed with. This note is written to be checked — it
explains the vocabulary our reports use, what each column can and cannot support, and the three
questions worth asking any vendor, including us.

If a report cannot survive these three questions, the format is doing the persuading and the
evidence is not.

---

## The vocabulary, and why it is not the usual vocabulary

### "Untriaged" is not "low"

An `Untriaged` item means a scanner matched a pattern and nobody has yet decided whether the
pattern reaches anything an attacker controls. It is the honest state of a machine's output.

Why it matters: a scanner that reports 174 hits and a report that prints "174 findings" are
describing two different worlds. In one of our own reviews, 174 hits collapsed to **one** item
worth a client's attention; 173 were patterns that a human ruled out, each with a written reason.

**Read it as:** "we have not finished thinking about this." Never as: "this is minor."

### "Withdrawn" is a decision, and it has to name its reversal

A withdrawal says a pattern is not a finding *here*. Every withdrawal in our library carries a
`what would change it` clause — the condition that would make it a finding again. For example:

> `B106` — placeholder secrets in test fixtures. **Withdrawn.** Would change if the same value
> could authenticate to any external service, or if a live credential had ever been committed.

**Read it as:** "this was looked at, and here is what would make me look again." A withdrawal
without that clause is an exit, not a judgement.

### "Design observation" is not a finding, and is still worth reading

Some properties are not defects — they are how the system is built, and their severity depends
entirely on what the customer does with it. Agent memory keyed by a tenant-supplied
`thread_id` is not a vulnerability; it becomes one the moment two tenants share a deployment and
the app trusts that key.

**Read it as:** "ask your engineers this question." These are often the most useful lines in the
document, because they are the ones a questionnaire cannot surface.

### "Severity depends on the app" is an answer, not a dodge

An LLM application's exposure is a function of its deployment: what tools it holds, whose data
it can read, whether a human approves actions. The same code can be a demo and a liability.
A report that assigns a fixed score to such a property is guessing with confidence.

---

## What each column can support

| Column | What it supports | What it does not |
|---|---|---|
| **Where** | the reviewer can open the file | it does not prove reachability |
| **What we observed** | a quotable fact | it is not an exploit |
| **What it costs the buyer** | a sentence for a security questionnaire | it is not a CVSS score |
| **Remediation** | a direction, not a patch | it does not prove the fix works |

Two absences are deliberate and worth noticing:

- **No payloads.** A report that hands over a working exploit is a report you cannot forward to
  your own engineers without also handing it to whoever reads their inbox.
- **No grades invented from scanner levels.** If a tool says `HIGH`, the report says the tool
  said `HIGH`. A person decides what it means, and the report names that person's reasoning.

---

## The three questions worth asking any vendor

1. **"Show me one thing you ruled out, and why."**
   A firm that cannot produce a withdrawal is not triaging; it is transcribing. The most
   informative page in any review is the one where the answer is "no".

2. **"Which of these did a human decide, and which did a tool decide?"**
   If the answer is "the tool", the report is a printout. If every line is "a human", ask how
   they kept the list short enough to finish — length is where judgement usually goes to die.

3. **"What is still unjudged?"**
   A confident document with no open items is usually a document that stopped asking. Ours
   prints its open items in their own column, and the verdict line counts them separately
   (`0 High · 5 Untriaged`) so the two cannot be confused.

---

## What a source review cannot tell you at all

This is the part sellers usually omit, so it is stated first here:

- **It cannot tell you what a deployed system does.** Source review reads code. A deployment
  with different configuration is a different system.
- **It cannot find the failures that matter most in an agent.** An instruction that arrives
  inside retrieved content, a tool output with no provenance, a tenant key the tenant controls
  — none of these are visible to a static analyzer. They are found by reading the trust
  boundaries and by testing the deployed path, which requires written authorisation and
  someone to run it.
- **It cannot certify anything.** No attestation, no warranty, no statement on behalf of
  maintainers. It is one reviewer's reasoning, published so it can be argued with.

If a vendor's document claims otherwise, that claim is the finding.

---

*Published by [Exhibitrail](https://github.com/contentforge-press/exhibitrail-assessments) —
Evidence, not adjectives. The four public assessments, the 24 tests and the pipeline are in this
repository; they can be re-run rather than believed.*
