# Release and verification

Read this before composing the ready-to-go handoff, then re-read it after Flo's go-ahead.

## Preconditions

- Reconfirm the Git remote, default branch, repository visibility, current branch, and disclosed mutation scope.
- Fetch origin and require a clean checkout, local `main` tracking `origin/main`, and both refs at the same commit before the first mutation. Stop and show the exact drift otherwise.
- Reconfirm kubectl context `admin@thecluster` before every mutation entrypoint.
- Require the disclosed Tunnel route and Access setup to be underway or complete, but do not probe the protected hostname before the Service exists.
- Stop if the contract, repository, cluster, or Cloudflare evidence has materially changed since the handoff.

## Implement and preflight

- Preserve user changes. Require the current checkout to be clean before changing branches or starting implementation; otherwise stop and ask Flo to resolve the existing state.
- Add the state-free container build, unprivileged runtime, `/healthz`, probes, resource requests and limits, and ClusterIP Service.
- Default static-runtime resources to 25m CPU and 32Mi memory requested, with 100m CPU and 64Mi memory limited; raise them only when measured app needs justify it.
- Disable service-account token mounting, privilege escalation, Linux capabilities, and writable root filesystems unless the runtime proves a narrow exception is required.
- Add ConfigMap and PVC mounts selected by the contract. Never put live contents in reusable manifests.
- Add the standard `just` interface and testable deploy/publisher code beside the app's existing scripts.
- Complete every local image and runtime-state safety check before pushing.
- Prioritize the smallest real production slice that can safely publish the state-free application. Never create a dummy package merely to initialize GHCR.

## GitHub Actions and GHCR

- GitHub Actions is the only registry publisher. Never log in to or push GHCR locally.
- Grant only `contents: read` and job-level `packages: write` unless an observed requirement proves more is needed.
- Attach `org.opencontainers.image.source` for the actual GitHub repository.
- Build only for image-relevant paths; include the dashboard's full monorepo-relative prefix when applicable. State-only changes must not build an image.
- Publish the full commit SHA from the onboarding branch and `main`; publish `latest` only from `main`.
- When the workflow is new and not yet on `main`, temporarily trigger the exact onboarding branch. Disclose and commit its later removal; never amend an already-published smoke commit merely to preserve a promised commit count.

For a new package:

1. Record `gh repo view` visibility and the confirmed `owner/package` identity.
2. Let the successful workflow create the package.
3. Match the exact owner, name, container type, source repository, and reviewed state-free SHA.
4. Open that package's settings page and ask Flo to perform the irreversible visibility confirmation at this early, disclosed checkpoint.
5. Verify package visibility with `gh api` and verify repository visibility is byte-for-byte unchanged.
6. Request a clean anonymous GHCR registry token and fetch the full-SHA manifest directly. Require the expected digest without using ambient Docker credentials or printing the token.

For an existing private package, perform the same early manual visibility handoff after matching its identity. Skip the handoff only when the exact package is already public, then still verify anonymous manifest access.

Never call an endpoint or UI control that changes repository visibility. If the package page, owner, name, confirmation copy, or browser authentication is ambiguous, stop for Flo.

## Smoke, merge, and deploy

1. Require successful onboarding-branch checks, image publication, package visibility, and anonymous manifest access.
2. Create the namespace and any persistent state resources without exposing a LoadBalancer, NodePort, or Ingress.
3. Deploy the exact branch SHA with no private state. Use the smallest synthetic fixture only when the UI cannot be meaningfully checked without runtime data.
4. Wait for readiness and verify the Service and EndpointSlice internally; use a temporary loopback-only port-forward when visual smoke review adds value.
5. Make one bounded anonymous request to the protected hostname. Require the expected Cloudflare Access redirect before publishing private state; report only status, login host, and pass/fail, never the signed query string.
6. Publish real state, restart the pod, and require ConfigMap/PVC state to survive.
7. Remove the temporary branch workflow trigger and commit the cleanup.
8. Fetch origin and re-require a clean checkout, local `main` equal to and tracking `origin/main`, unchanged remote ancestry, and `origin/main` as an ancestor of the reviewed HEAD.
9. Push the reviewed HEAD directly to remote `main` without force, fetch, switch to local `main`, fast-forward it to `origin/main`, and explicitly set or verify the `origin/main` upstream.
10. Require local `main`, `origin/main`, and the reviewed HEAD to be identical. Require successful main CI and confirm the full main SHA and `latest` resolve to the same digest.
11. Deploy the immutable main SHA, rerun state publication idempotently, and repeat health checks.
12. Delete only the merged remote branch. Do not delete or relocate the current checkout.

## Final verification

Require all of the following:

- Deployment image is the exact main SHA; pod, readiness, liveness, Service, and EndpointSlice are healthy.
- Kubernetes pulls the public image without an image-pull secret.
- Runtime state and assets are absent from the image and survive pod restart on their selected storage.
- `just dashboard-publish-state` succeeds idempotently and the Service returns the published hashes.
- Acquire or verify a fresh browser session immediately before checking that authenticated `https://<domain>` renders the real dashboard. If unavailable, finish automated verification and return one exact manual reload step without claiming the render was verified.
- Anonymous `/`, every state route, and representative media routes redirect to the expected Cloudflare Access login host. Keep redirect output terse and omit signed query strings.
- Source state, repository visibility, and unrelated files remain unchanged.
- Local `main`, its `origin/main` upstream, and the deployed immutable SHA agree.
- Any temporary uploader Pod and port-forward are gone; the protected hostname remains operational.

## Failure handling

- Branch CI failure: do not change package visibility, remove the branch trigger, or merge.
- Package-safety or visibility failure: do not deploy the image.
- Main CI failure: do not deploy main; fix forward.
- Deployment or public-route failure: redeploy the recorded known-good immutable SHA and preserve ConfigMaps and PVCs.
- First deployment without a known-good SHA: leave protected routing in place, preserve state resources, and report the failed SHA and exact verification stage.
- Unexpected Git state: stop further mutations, inspect refs and reflogs, and repair only a provably lossless fast-forward or upstream mismatch. Ask Flo before resolving divergence, overwriting changes, or discarding commits.
- Missing final browser session: do not block an otherwise verified release; report authenticated rendering as a precise manual remainder.
- Never roll back or delete runtime state automatically.
