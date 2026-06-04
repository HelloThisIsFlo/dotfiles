# Deployment Modes Reference

## Background

This document covers the three deployment modes available in our CD pipeline and the results of our testing to determine which mode works best in which scenario. The investigation was prompted by the incident on March 12th where a rolling deploy caused 3 minutes of mixed-version traffic that corrupted user sessions.

## The Three Modes

### Blue-Green Deploy

In a blue-green deployment, you maintain two identical production environments (blue and green). At any given time, only one is live. To deploy, you deploy the new version to the inactive environment, run smoke tests, and then switch the load balancer to point at it. If something goes wrong, you switch back.

The main advantage of blue-green is that the switchover is nearly instant (just a DNS/LB change) and rollback is equally fast. The main disadvantage is that you need to maintain two full production environments, which doubles your infrastructure cost. It also doesn't work well with database schema changes because both environments share the same database — if the new version requires a migration, rolling back means the old version needs to work with the new schema.

### Rolling Deploy

A rolling deployment gradually replaces instances of the old version with the new version. Typically you configure a maximum number of instances that can be unavailable during the deploy (maxUnavailable) and a maximum number of extra instances that can exist (maxSurge). Kubernetes handles this natively.

The advantage is that it's simple, uses minimal extra resources, and is the default in most orchestrators. The disadvantage is that during the deploy, you have mixed versions running simultaneously. This is fine for stateless services but can cause problems when there are breaking changes to the API contract between services, or when there are changes to session format, or when there are database schema changes.

### Canary Deploy

A canary deployment routes a small percentage of traffic (usually 1-5%) to the new version while the rest continues going to the old version. You monitor error rates and latency, and if everything looks good, you gradually increase the percentage until 100% of traffic is going to the new version.

The advantage is that you can catch problems with real production traffic while limiting the blast radius. The disadvantage is that it requires sophisticated traffic routing (usually a service mesh like Istio or Linkerd), it takes longer to complete a full rollout, and you still have the mixed-version problem during the rollout period.

## When to Use Each Mode

After testing all three modes extensively, here are our recommendations:

For stateless API services with no breaking changes, rolling deploy is fine. It's simple, resource-efficient, and the mixed-version window is short enough that it doesn't cause problems.

For stateful services or services with session affinity requirements, use blue-green deploy. The instant switchover eliminates the mixed-version problem entirely. Yes, it costs more, but the March 12th incident cost us more in engineering time than a year of extra infrastructure.

For high-traffic user-facing services where you want confidence before full rollout, use canary deploy. The ability to test with 1% of real traffic before committing is invaluable. This is especially important for services where the test environment doesn't accurately represent production load patterns.

Important: never use rolling deploy for services that modify shared state (databases, caches, message queues) unless the changes are fully backward-compatible. The mixed-version window will cause data corruption. We learned this the hard way on March 12th.

## Migration Path

If you're currently using rolling deploy and need to switch to blue-green or canary, the migration is straightforward. For blue-green, you need to provision a second environment and configure your load balancer for switchover. For canary, you need to set up Istio traffic splitting in the service mesh. Both migrations are documented in the platform team's runbook at docs/deploy-migration-runbook.md.

In conclusion, the choice of deployment mode should be driven by the statefulness of your service and the nature of your changes. When in doubt, prefer blue-green over rolling — the infrastructure cost is worth the peace of mind.
