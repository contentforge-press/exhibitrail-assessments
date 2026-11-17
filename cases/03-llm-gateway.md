# Case 3 — an LLM gateway, one decision on two paths

**Target:** `litellm` · proxy auth surface · 28,903 lines.
**Method:** read of the request-identity path, then trace of every consumer of the resulting address.

## Result

### M-1 — the same question answered two ways

`trusted_proxy_utils.py` fails **closed**: if it cannot establish that the request came through a
trusted proxy, the header-derived address is not trusted.

`auth_utils.get_request_ip_address()` still returns `x-forwarded-for` directly, and its
`is_internal_ip` check takes the leftmost value — the one a caller controls. A request from the
public internet can therefore be classified as internal and reach a non-public MCP server.

The bug is not a missing check. It is **an inconsistency between two implementations of the same
decision**, which is the failure mode that survives code review: each file looks correct alone.

### Positive

- `require_trusted_proxy_request` fails closed.
- Cold-start bypass is rejected when header and path disagree.

### Not published

The request shape that demonstrates the mismatch is deliberately omitted. A buyer needs to know the
path is inconsistent; the internet does not need a working payload.

## Limits

Source review of public code. No deployed proxy was tested.
