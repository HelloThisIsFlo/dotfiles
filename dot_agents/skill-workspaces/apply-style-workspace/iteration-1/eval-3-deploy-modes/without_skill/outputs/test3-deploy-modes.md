# Deployment Modes Reference

> Prompted by the March 12th incident: a rolling deploy caused 3 minutes of mixed-version traffic that corrupted user sessions.

---

## The Three Modes

### Blue-Green Deploy

Two identical production environments (blue and green); only one is live at a time.

**How it works:** Deploy to the inactive environment, run smoke tests, switch the load balancer.

| Pros | Cons |
|------|------|
| Near-instant switchover (DNS/LB change) | Doubles infrastructure cost (two full environments) |
| Equally fast rollback | Doesn't handle DB schema changes well -- both environments share one database, so rollback requires the old version to work with the new schema |

### Rolling Deploy

Gradually replaces old instances with new ones. Configured via `maxUnavailable` and `maxSurge`. Native to Kubernetes.

| Pros | Cons |
|------|------|
| Simple, resource-efficient | Mixed versions run simultaneously during deploy |
| Default in most orchestrators | Breaks on: API contract changes, session format changes, DB schema changes |

### Canary Deploy

Routes a small percentage of traffic (typically 1-5%) to the new version. Monitor error rates and latency, then gradually increase to 100%.

| Pros | Cons |
|------|------|
| Catches problems with real production traffic | Requires service mesh (Istio, Linkerd) |
| Limited blast radius | Slower full rollout |
| | Still has the mixed-version problem during rollout |

---

## When to Use Each Mode

| Scenario | Recommended Mode | Why |
|----------|-----------------|-----|
| Stateless API services, no breaking changes | **Rolling** | Simple, resource-efficient, mixed-version window is short enough |
| Stateful services or session affinity requirements | **Blue-Green** | Instant switchover eliminates mixed-version problem entirely |
| High-traffic user-facing services | **Canary** | Test with 1% of real traffic before committing -- especially valuable when test environments don't represent production load |

> **Warning:** Never use rolling deploy for services that modify shared state (databases, caches, message queues) unless changes are fully backward-compatible. The mixed-version window *will* cause data corruption. We learned this the hard way on March 12th.

---

## Migration Path

If you're currently on rolling deploy and need to switch:

- **To blue-green:** Provision a second environment, configure load balancer for switchover.
- **To canary:** Set up Istio traffic splitting in the service mesh.

Both migrations are documented in `docs/deploy-migration-runbook.md`.

**Bottom line:** Choose based on statefulness and change characteristics. When in doubt, prefer blue-green over rolling -- the infrastructure cost is worth the peace of mind.
