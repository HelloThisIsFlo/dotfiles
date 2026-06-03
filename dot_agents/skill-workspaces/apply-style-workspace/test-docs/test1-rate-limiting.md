# API Rate Limiting Strategies

## Introduction

In this document, we will explore the different rate limiting strategies available in our API gateway and discuss when each one should be used. It's important to note that choosing the wrong strategy can lead to either over-throttling legitimate users or allowing abuse to slip through. The information here is based on our load testing results from Q1 2026.

## Overview of Strategies

There are three main rate limiting strategies that our gateway supports:

### Fixed Window

The fixed window strategy divides time into fixed intervals (usually 1 minute or 1 hour) and counts the number of requests in each window. When the count exceeds the limit, subsequent requests are rejected until the next window starts. This is the simplest strategy to implement and understand, but it has a well-known problem: if a burst of traffic arrives right at the boundary between two windows, you can effectively get twice your rate limit in a short period. For example, if your limit is 100 requests per minute, a client could send 100 requests at 11:59:59 and another 100 at 12:00:01, resulting in 200 requests in 2 seconds.

### Sliding Window

The sliding window strategy addresses the boundary problem by calculating the rate based on a weighted average of the current and previous windows. This provides a much smoother rate limiting experience. The tradeoff is that it requires storing the previous window's count alongside the current one, which doubles the storage requirement. In our benchmarks, the sliding window added approximately 2ms of latency per request compared to fixed window, which is negligible for most use cases.

### Token Bucket

The token bucket strategy is the most flexible approach. It works by maintaining a "bucket" of tokens for each client. Tokens are added at a fixed rate, and each request consumes one token. If the bucket is empty, the request is rejected. The key advantage here is that it naturally allows short bursts while still enforcing an average rate. You can configure both the refill rate and the bucket size to control the burstiness. It's worth mentioning that this is the strategy used by most major cloud providers including AWS, Google Cloud, and Azure.

## Comparison

When comparing these strategies, there are several factors to consider. Fixed window is the simplest and has the lowest overhead, but the boundary problem can be a real issue for security-sensitive endpoints. Sliding window fixes the boundary problem with minimal additional complexity. Token bucket is the most flexible and is recommended for public-facing APIs where you want to allow occasional bursts.

It's also important to consider the storage requirements. Fixed window needs one counter per client per endpoint. Sliding window needs two counters. Token bucket needs a token count and a timestamp per client per endpoint.

## Our Recommendation

Based on our load testing and the analysis above, we recommend using the token bucket strategy for all new public-facing API endpoints. For internal service-to-service communication, the fixed window strategy is sufficient since the boundary problem is less of a concern when you control both sides of the connection. We should avoid using the sliding window strategy going forward as it offers a middle ground that isn't necessary given that token bucket is available — the sliding window is essentially a less capable version of token bucket with similar complexity.

Note: if you're migrating an existing endpoint from fixed window to token bucket, be careful about the initial bucket size. Setting it too high can cause a surge of previously-throttled requests. See the migration guide in docs/rate-limit-migration.md for the step-by-step process.

## Monitoring

In conclusion, regardless of which strategy you choose, you should monitor your rate limiting metrics closely. Key metrics to watch include the rejection rate (should be under 1% for well-configured limits), the p99 latency overhead (should be under 5ms), and the number of unique clients hitting limits (sudden spikes may indicate an attack). All of these metrics are available in the Grafana dashboard at grafana.internal/d/rate-limits.
