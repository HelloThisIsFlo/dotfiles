# Dashboard deployment contract

Use `DASHBOARD-DEPLOYMENT.yaml` to remember project-specific decisions so later runs stay quiet and deterministic.

## Location and authority

- Place the file at the dashboard workspace root, which may be below the Git root in a monorepo.
- Resolve `app_root` and state paths relative to that workspace.
- Keep stable personal-infrastructure defaults in the skill, not in every contract.
- Store no secrets, live state, temporary ports, image digests, commit SHAs, or credentials.
- Treat the contract as intended deployment configuration and live resources as observed state.
- When they conflict consequentially, report the exact drift and ask before changing either side.
- For a new deployment without a coherent contract or matching live resources, confirm its public identity with Flo before creating this file. Repository and app names may inspire options, but do not silently become the hostname or Kubernetes names.

## Version 1 shape

```yaml
version: 1
name: example-dashboard
domain: example.kempenich.ai
app_root: dashboard

state:
  mode: configmap
  files:
    - dashboard/public/state.json
  assets: []

image:
  name: example-dashboard

kubernetes:
  namespace: example-dashboard
  deployment: example-dashboard
  service: example-dashboard
```

## Field rules

- `version`
  - Must be `1`.
- `name`
  - Stable human and machine identity for the dashboard.
- `domain`
  - Full protected hostname under `kempenich.ai`.
- `app_root`
  - Application source path relative to the dashboard workspace.
- `state.mode`
  - One of `none`, `configmap`, `configmap-and-pvc`, or `existing-backend`.
- `state.files`
  - Generated textual runtime files. Empty for `none` or when an existing backend owns all state.
- `state.assets`
  - Generated binary or large runtime directories. Non-empty normally selects `configmap-and-pvc`.
- `image.name`
  - Lowercase GHCR package basename under `ghcr.io/hellothisisflo/`.
- `kubernetes.*`
  - DNS-safe names. Reuse one name when no existing convention requires distinct names.

For `existing-backend`, add only the durable fields needed to identify that backend and its persistence boundary. Do not design a generic database schema in this contract.

## Standard project interface

Create or preserve these `just` recipes:

- `dashboard-check`
  - Validate source state, types, and tests without publishing.
- `dashboard-build`
  - Produce the state-free production application.
- `dashboard-image-build`
  - Build a local-only `linux/amd64` image without registry authentication or push.
- `dashboard-deploy <full-sha>`
  - Guard `admin@thecluster`, apply reusable resources, deploy the immutable image, and wait for rollout.
- `dashboard-publish-state`
  - Validate, test, collect, publish every runtime state component, and verify what the Service serves.

The publisher remains independent from image rollout. For `state.mode: none`, the recipe still runs validation and confirms that no runtime state routes or mounts exist, then succeeds without a Kubernetes state mutation.

Update the contract only when a durable decision changes. Do not rewrite it merely because a deployment observed a new SHA, hash, pod, or timestamp.
