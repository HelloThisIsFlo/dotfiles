# Cache Invalidation Findings

We investigated how our caching layer behaves under various edge cases. The goal was to document surprising behaviors before the v2.0 migration.

## TTL Behavior

Our cache supports three TTL modes:

**Absolute TTL** expires entries at a fixed time after creation, regardless of access patterns. This is the most predictable mode.

**Sliding TTL** resets the expiration timer every time an entry is accessed. This keeps hot entries alive indefinitely, which is usually what you want for session data but can be dangerous for data that needs to be refreshed periodically.

**Adaptive TTL** automatically adjusts the TTL based on access frequency. Frequently accessed entries get longer TTLs, rarely accessed entries get shorter ones. The algorithm uses an exponential moving average with a configurable alpha parameter (default 0.3).

> [!important] When to use each mode
> Absolute TTL should be used for any data where staleness has business consequences — pricing data, feature flags, user permissions. Sliding TTL works well for session state and user preferences where you want to keep active users' data warm. Adaptive TTL is best for read-heavy caches where you want to minimize backend load without risking excessive staleness. The alpha parameter controls how quickly the TTL adapts: lower values (0.1-0.2) make it more conservative, higher values (0.4-0.5) make it more aggressive. In general, start with the default of 0.3 and adjust based on your cache hit ratio.

## Invalidation Edge Cases

### Thundering Herd on Expiry

When a popular cache entry expires, multiple concurrent requests will all miss the cache simultaneously and hit the backend. This is the classic thundering herd problem. We observed this causing up to 50x load spikes on the user-profile endpoint during peak hours. The solution is to use "stale-while-revalidate" — serve the stale entry while a single background request refreshes it.

### Race Condition on Write-Through

When using write-through caching, there's a subtle race condition. If a write and a read happen nearly simultaneously, the read might fetch the old value from the database and write it to the cache AFTER the write-through has already updated the cache with the new value. The result is that the cache contains stale data until the next TTL expiry.

This is especially problematic with sliding TTL because the stale entry will keep getting its TTL reset as long as it's being accessed, potentially keeping the stale data alive for hours or even days.

> [!warning] Critical interaction
> The combination of write-through caching and sliding TTL can result in stale data persisting indefinitely. If a cache entry is updated via write-through but a concurrent read overwrites it with stale data, the sliding TTL will keep the stale version alive as long as it's being accessed. This means that the more popular the data is, the longer the stale version persists — exactly the opposite of what you want. This is probably the most important finding from our investigation, and we strongly recommend that any endpoint using write-through caching should use absolute TTL, never sliding TTL.

### Partial Invalidation with Nested Objects

When a cached object contains nested references (e.g., a user object with embedded team data), invalidating the nested object doesn't automatically invalidate the parent. If you update a team's name, all cached user objects will still show the old team name until their own TTL expires.

We tested three approaches to this:
1. Eager invalidation — when a nested object changes, invalidate all parent objects. This is correct but expensive, requiring a reverse index of all parent-child relationships.
2. Version tags — attach a version number to each nested object and check it on cache hit. This catches staleness at read time but adds latency.
3. Short TTL on parents — keep parent object TTLs short (30-60s) so they naturally refresh. This is the simplest approach and works well when some staleness is acceptable.

For our use case, we went with approach 3 (short TTL on parents) combined with eager invalidation for the most critical relationships (user → permissions).

## Performance Impact

Overall, the caching layer reduces our p50 latency from 120ms to 8ms and our p99 from 450ms to 35ms. The cache hit ratio varies by endpoint but averages 94% across all endpoints. The memory overhead is approximately 2GB for our current dataset, which is well within our allocated resources.

See the full benchmark report at docs/cache-benchmarks.md for detailed numbers per endpoint.
