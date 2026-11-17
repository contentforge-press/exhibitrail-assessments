# Case 8 — AutoGen, 4,975 hits, no finding

**Target:** `microsoft/autogen` · 546 Python files · 112,463 lines (69,016 outside tests) ·
commit `8390985108cb1e3881f5f7297765758d8ad2540c` · cloned at depth 1, no running system touched.

**Method:** Bandit over the tree, every class of hit triaged, then a read of the paths the classes
point at: persistence, dynamic tool construction, container setup, benchmark downloads.

## Result

| | |
|---|---|
| Scanner hits | **4,975** |
| Real findings | **0** |
| Hits that are one repeated pattern | 4,897 (`assert` statements, B101) |
| Remaining hits worth reading | 78 |
| HIGH / MEDIUM reported by the scanner | 5 / 13 |

**A number this large is the argument for triage, not against the code.** 98.4% of the output is a
single test idiom. Of the 78 remaining hits, the ones that matter are design properties, and one is a
supply-chain note. Nothing here is a defect.

## What the 78 remaining hits resolve to

| Class | Count | Resolution |
|---|---|---|
| B101 assert | 4,897 | Test and validation idiom; one pattern, not 4,897 problems |
| B603 / B607 / B404 subprocess | 36 | Launching local tooling with a fixed argument list; no user string reaches a shell |
| B110 try-except-pass | 11 | Cleanup paths; no finding |
| B311 random | 7 | Sampling, not secrets |
| B324 MD5 | 4 | Content hashing for cache keys and ids; not a security decision |
| B104 bind 0.0.0.0 | 4 | Sample servers, in `samples/` |
| B105/B106/B107 hardcoded | 3 | Test fixtures |
| B301 pickle | 2 | See O-1 |
| B102 exec | 2 | See O-2 |
| B103 chmod 0o777 | 1 | See O-3 |
| B608 SQL string | 2 | **False positive** — the flagged lines build an import path and an error string, not a query |
| B113 timeout | 1 | Benchmark script |
| B615 HF revision pinning | 1 | See S-1 |

## O-1 — memory is persisted as pickle, and the directory is the boundary

`task_centric_memory/_memory_bank.py` restores memos with `pickle.load` from
`uid_memo_dict.pkl`; `_string_similarity_map.py` does the same for its map.

The write side is the same process, so the default deployment is consistent. The property worth
stating: **pickle turns "who can write to this directory" into "who can run code in the agent's
process."** If a memory directory is a mounted volume, a shared workspace, or a backup restored from
elsewhere, that is an execution boundary and should be treated as one — not as a cache directory.

This is a design observation, not a vulnerability: nothing in the repository accepts a remote pickle.

## O-2 — a tool can be built from a Python function at runtime

`autogen_core/tools/_function_tool.py` compiles a callable into source text (`to_code`) and `exec`s it
to reconstruct the function around line 171.

The input is a developer-supplied function already present in the process, so this is round-tripping,
not injection. The property worth stating: **the tool layer has a path where code is executed**, and
anything that widens what can reach `FunctionTool` — a plugin directory, a config pulled from a
service, a marketplace — inherits code execution without needing a separate bug.

## O-3 — the container executor widens a bind directory to 0o777

`docker_jupyter/_jupyter_server.py` does `os.chmod(bind_dir, 0o777)` so the container user can write
back. That is a deliberate trade for cross-container write access, and it is visible in one line.

The property worth stating: **a host directory becomes world-writable for the lifetime of the
executor**, and it is the same directory that carries notebook outputs back. On a single-user
workstation this is fine. On a shared host it is the difference between "the container can write"
and "any local user can".

## S-1 — one benchmark downloads without pinning a revision

`agbench/benchmarks/GAIA/Scripts/init_tasks.py` calls a Hugging Face snapshot download without a
revision. The other benchmark script (HumanEval) also calls `requests` without a timeout.

Both live under `agbench/`, not in the runtime packages, and both are authoring tools for benchmark
data. The note is about supply chain rather than runtime: **a dataset fetched at "latest" is a
dependency that can change under a fixed commit**, and a re-run is no longer reproducible. Pinning a
revision costs one argument.

## Positive

- `FunctionTool` input is a function object, not a string from the wire.
- The Docker executor is opt-in and named as such in the package layout (`autogen_ext/code_executors`).
- Studio validation returns typed `ValidationError` objects rather than swallowing exceptions.
- No SQL string construction reaches a query: the two B608 hits are import paths and messages.

## What this does not claim

No deployed system was touched. AutoGen's runtime behaviour under adversarial input is not tested
here; that is a different engagement with a written scope. A clean result means the source, at this
commit, produced no item that survived triage — it does not mean the product is safe, and it does not
mean a scanner with a different rule set would find nothing.

## Re-run

```bash
git clone --depth 1 https://github.com/microsoft/autogen
cd autogen && bandit -q -r . -f json -o /tmp/ag.json
python3 - <<'PY'
import json, collections
r = json.load(open('/tmp/ag.json'))['results']
print(len(r), collections.Counter(x['test_id'] for x in r).most_common(6))
PY
```
