# Deployment Modes Reference

Three CD pipeline modes. They look similar but behave very differently around **mixed-version traffic** — and the wrong choice corrupts state. 🫠

| Mode | Mechanism | Mixed versions? |
|------|-----------|-----------------|
| 🟦 `blue-green` | Two identical envs, LB switchover | **No** — instant cut |
| 🔄 `rolling` | Gradual instance replacement | **Yes** — during rollout window |
| 🐤 `canary` | %-based traffic splitting | **Yes** — during ramp-up |

> [!important] The rule
>
> - Stateful services or session affinity → 🟦 `blue-green`
> - Stateless APIs with backward-compatible changes → 🔄 `rolling`
> - High-traffic user-facing services needing production validation → 🐤 `canary`
> - Modifies shared state (DB, cache, message queue) with breaking changes? → **never** 🔄 `rolling`

## 🟦 Blue-Green

Maintain two identical production environments. Deploy to the inactive one, smoke test, switch the LB.

- **Switchover** — near-instant (DNS/LB change)
- **Rollback** — equally instant (switch back)
- **Cost** — doubles infrastructure (two full envs)
- ⚠️ **DB migrations** — both envs share one database => old version must work with new schema if you need to roll back

## 🔄 Rolling

Gradually replace old instances with new ones. Kubernetes-native via `maxUnavailable` / `maxSurge`.

- **Simple** — default in most orchestrators, minimal extra resources
- ⚠️ **Mixed-version window** — old and new run simultaneously during rollout
  - Fine for stateless services
  - 😤 Breaks on: API contract changes, session format changes, schema migrations

> [!warning] March 12th incident
>
> - Rolling deploy caused **3 minutes of mixed-version traffic**
> - Result: corrupted user sessions
> - Root cause: shared state mutation during mixed-version window
>
> => **Never use rolling for services that modify shared state unless changes are fully backward-compatible**

## 🐤 Canary

Route a small slice of traffic (1-5%) to the new version. Monitor error rates and latency, then gradually ramp to 100%.

- **Blast radius** — limited; catch problems with real production traffic
- **Requirements** — service mesh (Istio / Linkerd) for traffic splitting
- **Trade-offs**:
  - Slower full rollout
  - Still has mixed-version traffic during ramp-up
  - 🔑 Invaluable when test environments don't represent production load patterns

## Choosing a Mode

- 🔄 **Stateless API, no breaking changes** — `rolling` is fine. Simple, cheap, mixed-version window is short enough.
- 🟦 **Stateful / session-affinity services** — `blue-green`. Instant switchover eliminates mixed versions entirely. Yes it costs more — the March 12th incident cost more in engineering time than a year of extra infra.
- 🐤 **High-traffic user-facing** — `canary`. Testing with 1% of real traffic before committing is worth the complexity.

## Migration Path

- 🟦 **To blue-green** — provision second environment + configure LB switchover
- 🐤 **To canary** — set up Istio traffic splitting in the service mesh

> [!tip] Platform team runbook
>
> Both migrations are documented step-by-step in:
>
> - [deploy-migration-runbook.md](docs/deploy-migration-runbook.md)
