# Release and verification

Read this only after Flo's go-ahead to the ready-to-go handoff.

## Preconditions

- Reconfirm the Git remote, default branch, repository visibility, current branch, checkout state, and disclosed mutation scope.
- Reconfirm kubectl context `admin@thecluster` before every mutation entrypoint.
- Confirm the requested hostname anonymously redirects to Cloudflare Access before real state publication.
- Stop if the contract, repository, cluster, or Cloudflare evidence has materially changed since the handoff.

## Implement and preflight

- Preserve user changes. Require the current checkout to be clean before changing branches or starting implementation; otherwise stop and ask Flo to resolve the existing state.
- Add the state-free container build, unprivileged runtime, `/healthz`, probes, resource requests and limits, and ClusterIP Service.
- Default static-runtime resources to 25m CPU and 32Mi memory requested, with 100m CPU and 64Mi memory limited; raise them only when measured app needs justify it.
- Disable service-account token mounting, privilege escalation, Linux capabilities, and writable root filesystems unless the runtime proves a narrow exception is required.
- Add ConfigMap and PVC mounts selected by the contract. Never put live contents in reusable manifests.
- Add the standard `just` interface and testable deploy/publisher code beside the app's existing scripts.
- Complete every local image and runtime-state safety check before pushing.

## GitHub Actions and GHCR

- GitHub Actions is the only registry publisher. Never log in to or push GHCR locally.
- Grant only `contents: read` and job-level `packages: write` unless an observed requirement proves more is needed.
- Attach `org.opencontainers.image.source` for the actual GitHub repository.
- Build only for image-relevant paths; include the dashboard's full monorepo-relative prefix when applicable. State-only changes must not build an image.
- Publish the full commit SHA from the onboarding branch and `main`; publish `latest` only from `main`.
- When the workflow is new and not yet on `main`, temporarily trigger the exact onboarding branch. Remove that trigger before merging.

For a new package:

1. Record `gh repo view` visibility and the exact `owner/package` identity.
2. Let the successful workflow create the package.
3. Verify the published image is the reviewed state-free SHA.
4. Use an authenticated browser to change only that container package to public.
5. Verify package visibility with `gh api` and verify repository visibility is unchanged.

Never call an endpoint or UI control that changes repository visibility. If the package page, owner, name, confirmation copy, or browser authentication is ambiguous, stop for Flo.

## Smoke, merge, and deploy

1. Require successful onboarding-branch checks and image publication.
2. Create the namespace and any persistent state resources without exposing a LoadBalancer, NodePort, or Ingress.
3. Publish required initial runtime state, then deploy the exact branch SHA and wait for readiness.
4. Verify the Service and EndpointSlice internally; use a temporary loopback-only port-forward when visual smoke review adds value.
5. Restart the pod and require ConfigMap/PVC state to survive.
6. Remove the temporary branch workflow trigger and commit the cleanup.
7. Fetch origin, require the checkout to be clean and `origin/main` to be an ancestor of the reviewed HEAD, then fast-forward remote `main` from that exact HEAD and confirm it landed unchanged.
8. Require successful main CI. Confirm the full main SHA and `latest` resolve to the same digest.
9. Deploy the immutable main SHA, rerun state publication idempotently, and repeat health checks.
10. Delete only the merged remote branch. Do not delete or relocate the current checkout.

## Final verification

Require all of the following:

- Deployment image is the exact main SHA; pod, readiness, liveness, Service, and EndpointSlice are healthy.
- Kubernetes pulls the public image without an image-pull secret.
- Runtime state and assets are absent from the image and survive pod restart on their selected storage.
- `just dashboard-publish-state` succeeds idempotently and the Service returns the published hashes.
- Authenticated `https://<domain>` renders the real dashboard.
- Anonymous `/`, every state route, and representative media routes redirect to Cloudflare Access.
- Source state, repository visibility, and unrelated files remain unchanged.
- Any temporary uploader Pod and port-forward are gone; the protected hostname remains operational.

## Failure handling

- Branch CI failure: do not change package visibility, remove the branch trigger, or merge.
- Package-safety or visibility failure: do not deploy the image.
- Main CI failure: do not deploy main; fix forward.
- Deployment or public-route failure: redeploy the recorded known-good immutable SHA and preserve ConfigMaps and PVCs.
- First deployment without a known-good SHA: leave protected routing in place, preserve state resources, and report the failed SHA and exact verification stage.
- Never roll back or delete runtime state automatically.
