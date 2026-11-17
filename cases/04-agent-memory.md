# Case 4 — agent memory, a design observation

**Target:** `langgraph` · core `langgraph` 29,082 lines + checkpoint base and SQLite saver.
**Method:** read of the persistence resolution path.

**This case is a design observation, not a bug report.** The behaviour is documented and intentional.
It still decides whether a multi-tenant agent leaks conversations.

## D-1 — the key that separates tenants is a key the tenant controls

Every conversation is stored and fetched by exactly two values: `thread_id` and `checkpoint_ns`.

```sql
SELECT ... FROM checkpoints WHERE thread_id = ? AND checkpoint_ns = ?
```

There is no owner, tenant, principal or scope column anywhere in the resolution path.
`Pregel.get_state(config)` reads the thread id out of the caller-supplied config and hands it to
`checkpointer.get_tuple(config)`. Nothing validates who is asking.

Applications commonly pass the thread id from the client — a session id in a URL, a cookie, a form
field — because that is how a conversation is resumed. That value then selects the entire stored
history, message content included.

The library is a library; scope belongs to the application. But **the default shape of the API
invites the wrong decision**: a client-supplied session id is the path of least resistance, and it is
exactly the value that selects tenant data. Treat `thread_id` as a credential, not a name.

## Positive

- **P-1** `_own_checkpoint_config()` rewrites the checkpoint namespace for subgraphs that carry their
  own checkpointer, reconstructing it from the parent path. A caller cannot inject an arbitrary
  namespace through config. The codebase does think about config injection — just not about identity.
- **P-2** `delete_thread()` and `delete_for_runs()` are first-class operations, not raw SQL left to
  the developer. A retention promise can actually be executed against this store.

## Limits

No exploit is described, because none exists here — it is a responsibility boundary. Severity
depends entirely on how the consuming application builds its session model.
