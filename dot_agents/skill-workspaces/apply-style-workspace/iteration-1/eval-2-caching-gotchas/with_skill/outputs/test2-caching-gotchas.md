# Cache Invalidation Gotchas

Our caching layer has surprising behaviors under edge cases. Documented before the v2.0 migration.

## TTL Modes

Three TTL modes, very different trade-offs:

| Mode | Behavior |
|------|----------|
| ✅ `absolute` | Expires at fixed time after creation — most predictable |
| 🔄 `sliding` | Resets expiration on every access — keeps hot entries alive indefinitely |
| ⚠️ `adaptive` | Auto-adjusts TTL based on access frequency (exponential moving average, default `alpha=0.3`) |

> [!important] When to use each mode
>
> - ✅ `absolute` → data where staleness has business consequences (pricing, feature flags, permissions)
> - 🔄 `sliding` → session state, user preferences — keep active users' data warm
> - ⚠️ `adaptive` → read-heavy caches where you want to minimize backend load without excessive staleness
>   - `alpha` controls adaptation speed: `0.1-0.2` = conservative, `0.4-0.5` = aggressive
>   - Start with `0.3`, adjust based on cache hit ratio

## Invalidation Edge Cases

### ⚡ Thundering Herd on Expiry

When a popular entry expires, all concurrent requests miss simultaneously and slam the backend.

- Observed **50x load spikes** on the user-profile endpoint during peak hours
- Fix: **stale-while-revalidate** — serve stale entry while a single background request refreshes it

### 🤯 Race Condition on Write-Through

Subtle but nasty. With write-through caching, a near-simultaneous read can overwrite the fresh cache value with stale data:

1. Write-through updates cache with **new** value
2. Concurrent read fetches **old** value from DB
3. Read writes **old** value to cache AFTER the write-through
4. Cache now contains stale data until next TTL expiry

> [!warning] Write-through + sliding TTL = stale data forever
>
> - The stale entry keeps getting its TTL reset on every access
> - More popular the data => longer the stale version persists — exactly backwards
> - This was the most critical finding from the investigation
>
> **Any endpoint using write-through caching MUST use `absolute` TTL, never `sliding`.**

### 😤 Partial Invalidation with Nested Objects

When a cached object contains nested references (e.g., user with embedded team data), invalidating the nested object does **not** invalidate the parent. Update a team's name => all cached user objects still show the old name until their own TTL expires.

Three approaches tested:

| Approach | Trade-off |
|----------|-----------|
| **Eager invalidation** | Correct but expensive — requires reverse index of all parent-child relationships |
| **Version tags** | Catches staleness at read time but adds latency on every cache hit |
| **Short TTL on parents** | Simplest — 30-60s TTL, works when some staleness is acceptable |

> [!important] Our approach
>
> - **Short TTL on parents** as the default (simplest, good enough for most cases)
> - **Eager invalidation** for critical relationships only (`user` → `permissions`)

## Performance Impact

- **p50 latency**: 120ms → **8ms**
- **p99 latency**: 450ms → **35ms**
- **Cache hit ratio**: 94% average across all endpoints
- **Memory overhead**: ~2GB (within allocated resources)

---

_For detailed per-endpoint numbers, see [docs/cache-benchmarks.md](docs/cache-benchmarks.md)._
