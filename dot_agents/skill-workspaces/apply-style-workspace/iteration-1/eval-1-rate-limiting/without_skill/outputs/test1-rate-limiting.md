# API Rate Limiting Strategies

> Based on load testing results from Q1 2026.

Choosing the wrong strategy can lead to over-throttling legitimate users or allowing abuse to slip through. This document covers the three strategies our API gateway supports and when to use each one.

---

## Strategies

### Fixed Window

Divides time into fixed intervals (typically 1 minute or 1 hour) and counts requests per window. Requests beyond the limit are rejected until the next window starts.

- **Pros:** Simplest to implement, lowest overhead
- **Cons:** Boundary problem — a burst at the window edge can double the effective rate
  - Example: With a 100 req/min limit, a client sends 100 requests at 11:59:59 and another 100 at 12:00:01 — 200 requests in 2 seconds

### Sliding Window

Calculates the rate using a weighted average of the current and previous windows, eliminating the boundary problem.

- **Pros:** Much smoother rate limiting, minimal added complexity
- **Cons:** Doubles storage (must retain previous window's count)
- **Latency overhead:** ~2ms per request vs. fixed window (negligible for most use cases)

### Token Bucket

Maintains a "bucket" of tokens per client. Tokens refill at a fixed rate; each request consumes one token. Empty bucket = rejected request.

- **Pros:** Most flexible — naturally allows short bursts while enforcing an average rate
- **Configurable:** Both refill rate and bucket size control burstiness
- **Industry standard:** Used by AWS, Google Cloud, and Azure

---

## Comparison

| Factor | Fixed Window | Sliding Window | Token Bucket |
|---|---|---|---|
| **Complexity** | Lowest | Moderate | Moderate |
| **Boundary problem** | Yes | No | No |
| **Burst support** | No | No | Yes (configurable) |
| **Storage per client/endpoint** | 1 counter | 2 counters | 1 token count + 1 timestamp |

---

## Recommendation

| Use Case | Strategy | Rationale |
|---|---|---|
| **Public-facing APIs** (new endpoints) | Token bucket | Flexible, handles bursts, industry standard |
| **Internal service-to-service** | Fixed window | Sufficient when you control both sides |
| **Sliding window** | Avoid going forward | Middle ground that isn't needed when token bucket is available |

### Migration note

When migrating from fixed window to token bucket, be careful with the initial bucket size. Setting it too high can cause a surge of previously-throttled requests. See `docs/rate-limit-migration.md` for the step-by-step process.

---

## Monitoring

Regardless of strategy, monitor these key metrics:

| Metric | Target |
|---|---|
| **Rejection rate** | < 1% for well-configured limits |
| **p99 latency overhead** | < 5ms |
| **Unique clients hitting limits** | Watch for sudden spikes (may indicate an attack) |

Dashboard: [grafana.internal/d/rate-limits](http://grafana.internal/d/rate-limits)
