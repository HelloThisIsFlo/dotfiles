# API Rate Limiting Strategies

Three strategies, very different trade-offs. Based on Q1 2026 load testing.

| Strategy | Behavior | Storage |
|----------|----------|---------|
| 🔄 `fixed_window` | Counts requests per fixed interval (1min / 1hr), rejects above limit | 1 counter per client per endpoint |
| ✅ `sliding_window` | Weighted average of current + previous window — smooths boundaries | 2 counters per client per endpoint |
| ⚡ `token_bucket` | Bucket of tokens, refills at fixed rate, each request drains one | 1 token count + 1 timestamp per client per endpoint |

> [!important] The rule
>
> - Public-facing APIs → ⚡ `token_bucket` (recommended default)
> - Internal service-to-service → 🔄 `fixed_window` (sufficient when you control both sides)
> - 🚫 `sliding_window` → avoid going forward — it's a less capable `token_bucket` with similar complexity

## 🔄 Fixed Window

Simplest strategy — divide time into intervals, count requests, reject when over limit.

- **Boundary problem** — burst at window edges can double effective throughput
  - **Example:** limit = 100 req/min, client sends 100 at `11:59:59` + 100 at `12:00:01` => 200 requests in 2 seconds 😤

> [!warning] Window boundary exploit
>
> - Clients can get **2x the rate limit** by timing requests across a window boundary
> - Security-sensitive endpoints should NOT use fixed window

## ✅ Sliding Window

Fixes the boundary problem by weighting current + previous window counts.

- +2ms latency per request vs fixed window — negligible for most use cases
- 2x storage (stores both current and previous window counts)

## ⚡ Token Bucket

Most flexible — naturally allows short bursts while enforcing average rate.

- Bucket fills at a constant rate, each request drains one token, empty bucket = rejected
- Two knobs: **refill rate** (average throughput) and **bucket size** (burst allowance)
- Industry standard — used by AWS, Google Cloud, and Azure

## Migration

> [!warning] Migrating from fixed window to token bucket?
>
> - **Initial bucket size matters** — too high causes a surge of previously-throttled requests
> - Ramp up gradually
>
> _See [docs/rate-limit-migration.md](docs/rate-limit-migration.md) for the step-by-step process._

## Monitoring

Key metrics to watch regardless of strategy:

- **Rejection rate** — should be under 1% for well-configured limits
- **p99 latency overhead** — should be under 5ms
- **Unique clients hitting limits** — sudden spikes may indicate an attack

> [!tip] Grafana dashboard
>
> All rate limiting metrics available at [grafana.internal/d/rate-limits](grafana.internal/d/rate-limits)
