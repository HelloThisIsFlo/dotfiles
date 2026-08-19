# State and public-image safety

Choose storage from the app's existing state boundary. Do not invent a backend for a static dashboard or flatten a real backend into files.

## Selection

| Evidence | Mode | Runtime treatment |
|---|---|---|
| No generated or private runtime data | `none` | Serve the state-free image only |
| Text files comfortably below the Kubernetes object limit | `configmap` | Mount a ConfigMap directory outside image assets |
| Text state plus generated media or other large files | `configmap-and-pvc` | ConfigMap for text; `nfs-client` PVC for assets |
| Existing API, database, or hosted service owns state | `existing-backend` | Preserve it and make persistence/credentials explicit |

Use a conservative ceiling of 750 KiB for the complete serialized ConfigMap. Never base64 large assets into ConfigMaps or Secrets. If text state approaches the ceiling, use the PVC or the existing backend.

## State-free public image

- A public image contains application code and explicitly public, repository-tracked presentation assets only.
- Generated state, user-derived media, local databases, credentials, source documents, Git data, dependencies, and local build output stay outside its context and layers.
- A dashboard-safe asset is not automatically safe for a public registry layer.
- If application code or licensed assets themselves may not be publicly distributable, stop instead of making the package public.
- Use a separate production build command that does not collect state.
- Use a multi-stage `linux/amd64` build and an unprivileged runtime.
- Serve `/healthz` independently of runtime state.
- Serve runtime files from separate mounted directories with `Cache-Control: no-store` where freshness matters.

Before package publication:

1. Run source validation, types, tests, and the state-free production build.
2. Build a local-only image without GHCR authentication.
3. Inspect the Docker context, history, layers, and served filesystem for known state and asset paths.
4. Require state routes to return the intended missing-state response without mounts.
5. Mount synthetic runtime data locally and verify the real UI, state routes, media routes, and health endpoint.

## ConfigMap publication

- Keep ConfigMap contents out of reusable tracked manifests.
- Mount the ConfigMap as a directory, not with `subPath`.
- Validate and collect locally before the first Kubernetes mutation.
- Distinguish collector determinism from publisher idempotence:
  - When unchanged authored state represents the same snapshot, collect twice locally and require identical state hashes.
  - Avoid current-clock fields that create meaningless churn; retain them only when publication time is intentional dashboard content.
  - When volatile output is intentional, report that semantic choice instead of misclassifying it as an idempotence failure.
- Apply the exact collected bytes.
- Wait until every desired ready pod exposes the expected SHA-256.
- Fetch the state through the ClusterIP Service and require matching bytes.
- When the target already contains the exact collected bytes, skip unnecessary ConfigMap mutation and still complete served-state verification.
- On failure, report expected and observed hashes without automatic rollback.

## ConfigMap plus PVC publication

Use the small text state as the publication boundary and publish referenced assets before it.

1. Validate sources, asset approvals, path containment, and supported types.
2. Collect ignored JSON and media output locally.
3. Calculate a manifest of relative paths, sizes, and SHA-256 hashes.
4. Require the target namespace and a Bound `nfs-client` PVC.
5. Create a temporary uploader Pod that mounts the PVC; do not depend on an existing application pod for initial publication.
6. Upload changed or new files to temporary paths and atomically rename each verified file into place.
7. Apply the ConfigMap text state only after every referenced asset is present.
8. Wait for pod projection, then verify state bytes and representative asset hashes through the Service.
9. Remove assets no longer referenced only after the new state is verified; update the PVC manifest last.
10. Remove the uploader Pod. Preserve the PVC and last verified state on failure.

An identical publish must avoid recopying unchanged assets or rewriting identical state and must still complete verification. Test collection determinism locally; do not require two full cluster publications merely to prove it.

## Existing backend escape hatch

- Keep a hosted API or database when it genuinely owns state.
- Put a local persistent database file on a PVC rather than a ConfigMap.
- Keep credentials in Kubernetes Secrets or the backend's existing secret system, never in the deployment contract.
- Ask Flo only when data migration, persistence, credentials, or public-image safety cannot be derived safely.
