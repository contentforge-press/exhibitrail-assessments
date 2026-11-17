# Data

## `trust-center-coverage.csv`

106 domains in our addressable set, eight topics, one row each, values 0/1.

- `readable=0` — the trust or compliance page could not be fetched; excluded from every
  denominator in [case 06](../cases/06-trust-centers.md). 101 of 106 were readable.
- A `0` means **the string did not appear on the page**. It does not mean the control is
  missing. A page can answer in other words ("untrusted content" for a prompt-injection
  control). This counts vocabulary, not quality.

Reproduce it:

```sh
python3 tools/trust_center_survey.py --domains domains.txt --out coverage.csv
```

`domains.txt` is one domain per line. The survey follows the same paths the original run used
(`/trust`, `/security`, `/compliance`, `/privacy`, plus `trust.` and `security.` subdomains)
and keeps the first page that mentions at least two trust-center markers.

## Snapshot, citation, changes

- [CITATION.md](CITATION.md) — cite a commit, not the branch. Also the four rules we hold
  ourselves to when this number is quoted.
- [CHANGELOG.md](CHANGELOG.md) — what changed, and the four known weaknesses recorded at
  snapshot 1 so a later version can be judged against them.

## Why publish the per-domain matrix

Because a number nobody can recompute is an adjective. If you disagree with a `0`, fetch the
page and see for yourself — that is the point of the column.
