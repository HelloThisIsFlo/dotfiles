# Cache Invalidation Findings

Investigation of caching layer edge cases, documented before the v2.0 migration.

---

## TTL Modes

Our cache supports three TTL modes:

### Absolute TTL

Expires entries at a fixed time after creation, regardless of access patterns. Most predictable mode.

### Sliding TTL

Resets the expiration timer on every access. Keeps hot entries alive indefinitely.

- **Good for:** session data, user preferences (keeps active users' data warm)
- **Dangerous for:** data that needs periodic refresh

### Adaptive TTL

Automatically adjusts TTL based on access frequency using an exponential moving average.

- Frequently accessed entries get longer TTLs
- Rarely accessed entries get shorter ones
- Configurable alpha parameter (default: 0.3)
  - Conservative: 0.1--0.2
  - Aggressive: 0.4--0.5
- Best for read-heavy caches where you want to minimize backend load without excessive staleness

> [!important] When to use each mode
>
> - **Absolute** -- data where staleness has business consequences (pricing, feature flags, permissions)
> - **Sliding** -- session state, user preferences
> - **Adaptive** -- read-heavy caches; start with alpha=0.3, tune based on hit ratio

---

## Invalidation Edge Cases

### Thundering Herd on Expiry

When a popular cache entry expires, multiple concurrent requests all miss simultaneously and hit the backend.

- Observed **up to 50x load spikes** on the user-profile endpoint during peak hours
- **Solution:** stale-while-revalidate -- serve the stale entry while a single background request refreshes it

### Race Condition on Write-Through

Subtle race when a write and a read happen nearly simultaneously:

1. Write-through updates cache with new value
2. Concurrent read fetches old value from database
3. Read writes old value back to cache, **overwriting** the new value
4. Cache now contains stale data until next TTL expiry

> [!warning] Critical: write-through + sliding TTL
>
> This combination can cause **stale data to persist indefinitely**. The stale entry keeps getting its TTL reset on every access, meaning the more popular the data, the longer the stale version lives -- exactly the opposite of what you want.
>
> **Recommendation:** Any endpoint using write-through caching should use **absolute TTL**, never sliding TTL.

### Partial Invalidation with Nested Objects

When a cached object contains nested references (e.g., user with embedded team data), invalidating the nested object does not automatically invalidate the parent. Updating a team's name leaves all cached user objects showing the old name until their own TTL expires.

**Three approaches tested:**

| Approach | Mechanism | Trade-off |
|---|---|---|
| **Eager invalidation** | Invalidate all parents when a nested object changes | Correct but expensive; requires reverse index of all parent-child relationships |
| **Version tags** | Attach version number to nested objects, check on cache hit | Catches staleness at read time but adds latency |
| **Short TTL on parents** | Keep parent TTLs short (30--60s) for natural refresh | Simplest; works when some staleness is acceptable |

**Our choice:** Short TTL on parents (approach 3) combined with eager invalidation for critical relationships (user -> permissions).

---

## Performance Impact

| Metric | Without cache | With cache |
|---|---|---|
| p50 latency | 120ms | 8ms |
| p99 latency | 450ms | 35ms |
| Cache hit ratio | -- | 94% avg across endpoints |
| Memory overhead | -- | ~2GB |

See `docs/cache-benchmarks.md` for detailed per-endpoint numbers.
