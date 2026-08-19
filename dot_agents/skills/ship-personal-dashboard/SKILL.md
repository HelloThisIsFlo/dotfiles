---
name: ship-personal-dashboard
description: Turn Flo's local personal dashboard prototypes into protected deployments on his home Kubernetes cluster through GHCR, Kubernetes, Cloudflare Tunnel, and Access. Use when Flo wants to host, expose, publish, or move a local dashboard to a kempenich.ai hostname; discover the real repository and state shape first, ask only for unresolved consequential choices, and run the disclosed release end to end only after Flo's go-ahead.
---

# Ship Personal Dashboard

Turn a working local prototype into a durable, one-user service without making its source repository, runtime state, or generated assets public.

## Fixed platform

Default to Flo's existing personal infrastructure:

- kubectl context `admin@thecluster`
- GHCR owner `HelloThisIsFlo`
- private Git source and a state-free public container image
- `linux/amd64`, one unprivileged replica, and a ClusterIP Service
- container port `8080`, Service port `80`, and `/healthz` probes
- `nfs-client` when persistent file storage is required
- the existing Cloudflare Tunnel and Access policy under `*.kempenich.ai`
- a feature branch followed by a fast-forward merge to `main`

Do not generalise these defaults into provider choices. Inspect for conflicts and ask only when a project genuinely cannot use this platform.

## Permission gate

Discovery is read-only. It does not authorize repository edits, commits, pushes, package changes, Kubernetes mutations, or Cloudflare changes.

Before any mutation, give Flo one **ready-to-go handoff** that discloses the complete run and wait for an explicit go-ahead. End the handoff with a clear **Your part** section so every expected Flo action is visible before the run starts.

That go-ahead authorizes only the actions listed in the handoff, including implementation, commits, pushes, package publication, fast-forward merge, deployment, state publication, verification, and merged remote-branch cleanup. Pause for an undisclosed expansion, a failed safety gate, authentication required for a remaining mutation, or an external action that cannot be completed safely.

## Discover before asking

1. Locate the actual Git root and dashboard workspace. Read their instruction files.
2. Read `DASHBOARD-DEPLOYMENT.yaml` from the dashboard workspace when it exists.
3. Inspect, without mutation:
   - framework, build output, runtime server, health route, and existing `just` recipes
   - authored sources, generated JSON, media, secrets, databases, and external backends
   - Docker, Actions, Kubernetes, deployment scripts, and ignored outputs
   - Git privacy, remote, default branch, current branch, dirty state, and monorepo-relative paths
   - GHCR package existence and visibility
   - cluster context, name collisions, `nfs-client`, and the existing `cloudflared` deployment
4. Read [deployment-contract.md](references/deployment-contract.md) when the contract is missing, incomplete, or contradicted.
5. Read [state-and-image-safety.md](references/state-and-image-safety.md) when the app has generated state, media, secrets, a database, or an existing backend.
6. Read [release-and-verification.md](references/release-and-verification.md) completely before composing the ready-to-go handoff so its release order, rollback, and cleanup match execution.

Infer technical answers from evidence, but do not silently invent a new deployment's public identity. When a coherent contract or matching existing deployment does not already establish it, pause after discovery for one compact naming checkpoint:

- Offer two or three coherent, evidence-based naming bundles, with the recommended option first.
- Show the protected hostname, Kubernetes namespace, and shared base name for the image, Deployment, and Service in each bundle.
- Let Flo choose, mix, or rename the options.
- Include any other unresolved consequential choice in the same checkpoint when practical.

After Flo confirms the names, use them in the ready-to-go handoff and later contract. Do not present the full handoff before that confirmation. Never repeat an answer already recorded in a coherent contract or established by a matching deployment.

Outside this naming checkpoint, ask only when an unresolved choice would change public-image safety, storage, release path, or destructive scope.

## Ready-to-go handoff

Before asking Flo to proceed, report:

- protected URL and chosen subdomain
- exact Tunnel route: `https://<hostname>` to `http://<service>.<namespace>.svc.cluster.local:80`
- hostname to add to the existing Access application and policy
- image name, Git root, dashboard workspace, branch path, and package-visibility status
- Kubernetes namespace, Deployment, Service, and state mode
- standard `just` commands that will be added or preserved
- smoke path, final verification, rollback target, and cleanup
- every commit, push, merge, browser mutation, and cluster mutation the go-ahead will authorize

Preserve the last valid ConfigMap and PVC contents during rollback. Never promise automatic runtime-state deletion or rollback. For a first deployment without a known-good image, preserve protected routing and diagnostic resources rather than inventing a destructive rollback.

End with **Your part**:

- **After saying go ahead:** configure the exact Tunnel route and Access hostname while the agent preflights and publishes the first real state-free image through GitHub Actions.
- **Expected early pause:** when the exact GHCR package is new or private, the agent opens its package settings and Flo performs the irreversible visibility confirmation. Skip this only when that package is already public; repository visibility does not decide package visibility.
- **Possible final check:** manually reload the authenticated dashboard only when the agent cannot acquire a fresh browser session for final QA.

Do not require Cloudflare setup before the go-ahead. Run package initialization and Flo's Cloudflare setup in parallel. A missing origin is expected until the Service exists.

## Execute after go-ahead

Re-read [release-and-verification.md](references/release-and-verification.md), then execute the disclosed run persistently.

- Preserve unrelated changes and require a clean checkout before changing branches, committing, or pushing.
- Add or update `DASHBOARD-DEPLOYMENT.yaml` with durable, non-secret decisions.
- Adapt the implementation to the actual app; do not copy one dashboard's schema into another.
- Make GitHub Actions the only GHCR publisher. Local image builds are preflight only.
- Deploy immutable commit SHA tags, never `latest`.
- Deploy the state-free application with empty or synthetic state, prove Access protection, and only then publish private state.
- Publish every valid runtime snapshot through `just dashboard-publish-state`.
- Pause when continuing would risk private data, corrupt Git, deploy an unverified image, or require an external action. Continue independent safe work through non-blocking QA gaps and preserve the last valid ConfigMap, PVC contents, and deployed image.

## Finish

Return the protected URL and a short ledger: main SHA, image digest, Kubernetes health, published-state hash, Access behavior, repository visibility, package visibility, cleanup, and any precise manual QA remainder. Distinguish verified results from manual checks.
