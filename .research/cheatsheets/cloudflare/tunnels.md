# Cloudflare Tunnels — Cheat Sheet

You want to expose a service running on a machine (laptop, NAS, home cluster) to the public internet without opening firewall ports, dealing with dynamic DNS, or punching holes through your router. A Cloudflare Tunnel makes the box itself dial *outward* to Cloudflare's edge over TLS, and Cloudflare proxies inbound requests for your hostnames back through that connection. No inbound ports. No public IP needed. Free for personal use.

---

## Mental model

Three things, three layers:

1. **Tunnel** — a named, long-lived outbound connection from your box to Cloudflare. Lives in your CF account. Has a UUID and a name (e.g. `TheMac`, `TheHome - HAOS`).
2. **Connector** — `cloudflared` running on a machine, authenticated to the tunnel. One tunnel can have multiple connectors (HA — see [Multi-connector](#multi-connector--ha)).
3. **Ingress rules** — "when request comes in for `foo.kempenich.dev`, forward it to `http://localhost:8000`." Lives either in a local YAML file (CLI mode) or in the Zero Trust dashboard.

DNS layer is separate but bound: a CNAME at `foo.kempenich.dev` points at `<tunnel-uuid>.cfargotunnel.com`. That's how Cloudflare's edge knows to forward inbound requests for that hostname to your tunnel.

---

## Auth model (this trips everyone up)

Two distinct credential files in `~/.cloudflared/`:

| File | Scope | When created | What dies if you lose it |
|---|---|---|---|
| `cert.pem` | **Account-level**. Lets you create/delete/manage tunnels for your CF account. | `cloudflared tunnel login` (once, ever) | Can't manage tunnels until you re-login |
| `<UUID>.json` | **Tunnel-level**. Authorises a connector to RUN one specific tunnel. | `cloudflared tunnel create <name>` | That tunnel can't run — recreate or rotate |

Rule of thumb: `cert.pem` is the **admin key** (rare use, sensitive). The `.json` is the **runtime key** (used every time the tunnel starts).

> **Recreate a tunnel → new UUID → new `.json`.** Old `.json` lingers in `~/.cloudflared/` doing nothing. Delete it manually when you're done.

---

## Three ways to run a tunnel

You actually use all three. Each has a niche.

### 1. CLI config file (TheMac pattern)

You hand-edit a YAML, point `cloudflared` at it, and run it yourself. Source-controllable (via chezmoi).

```yaml
# ~/.cloudflared/config-themac.yml
tunnel: a57f23b6-310d-40bd-b061-e62ecfee83f3
credentials-file: /Users/flo/.cloudflared/a57f23b6-310d-40bd-b061-e62ecfee83f3.json

ingress:
  - hostname: sketchpad.kempenich.dev
    service: http://localhost:8000
  - hostname: outpost.kempenich.dev
    service: http://localhost:8080
  - service: http_status:404   # catch-all REQUIRED
```

Run it:
```bash
cloudflared tunnel --config ~/.cloudflared/config-themac.yml run TheMac
```

**Use when:** local dev on a workstation you own. Fast iteration on ingress rules. Config in dotfiles repo.

### 2. Dashboard-managed (your home clusters)

You create the tunnel in CF Zero Trust dashboard, copy a one-shot token, paste it where the connector runs. All ingress rules + DNS routes managed in the UI.

```bash
cloudflared tunnel run --token <very-long-token>
```

No local config file. The token IS the credentials — anyone with it can run the tunnel. Treat it like a secret.

**Use when:** long-lived infra (servers, NAS, K8s nodes). You want changes via UI, not SSH-and-edit-YAML. Multiple people may manage routes.

### 3. Embedded (HAOS add-on, K8s deployment)

A platform-specific wrapper around mode #2 (token-based). The wrapper handles install, autostart, secrets:

- **Home Assistant**: `Cloudflared` add-on, paste token in add-on config
- **Kubernetes**: official helm chart `cloudflare/cloudflare-tunnel`, token via secret

You don't touch `cloudflared` directly — the platform owns its lifecycle.

**Use when:** the host platform has an opinionated wrapper. Don't fight it.

---

## Tunnel CRUD

The commands you actually use. All operate on your CF account via `cert.pem`.

```bash
cloudflared tunnel login                  # once ever — writes cert.pem
cloudflared tunnel create <name>          # creates tunnel + writes <uuid>.json
cloudflared tunnel list                   # all tunnels + their UUIDs + active connectors
cloudflared tunnel info <name>            # detailed status of one tunnel
cloudflared tunnel delete <name>          # remove (fails if connectors still active — pass --force)
cloudflared tunnel run <name>             # start a connector (uses ~/.cloudflared/config.yml by default)
```

> **Naming with spaces:** dashboard-managed tunnels often have spaces (`TheHome - HAOS`). Quote them: `cloudflared tunnel info "TheHome - HAOS"`.

---

## Ingress rules (the YAML)

First match wins. Catch-all is mandatory or `cloudflared` won't start.

```yaml
ingress:
  - hostname: api.kempenich.dev
    service: http://localhost:3000

  - hostname: blog.kempenich.dev
    path: /admin/.*
    service: http://localhost:4000      # admin path → different backend

  - hostname: blog.kempenich.dev
    service: http://localhost:5000      # everything else on blog → main backend

  - service: http_status:404            # catch-all (required)
```

Common `service:` values:

| Value | Use |
|---|---|
| `http://localhost:PORT` | Plain HTTP origin |
| `https://localhost:PORT` | HTTPS origin (CF terminates inbound TLS, re-encrypts to origin) |
| `ssh://localhost:22` | SSH (see [Non-HTTP origins](#non-http-origins)) |
| `tcp://localhost:PORT` | Raw TCP (databases, custom protocols) |
| `unix:/var/run/foo.sock` | Unix domain socket |
| `http_status:404` | Always return this status (typical catch-all) |
| `hello_world` | CF's built-in test server (debugging) |

> **`originRequest` block:** add per-rule options like `noTLSVerify: true` (skip cert check on origin), `connectTimeout`, `httpHostHeader` (override Host header). Niche — you'll know when you need it.

---

## DNS routing

Tunnels don't auto-create DNS records. You point a CNAME at the tunnel separately.

```bash
cloudflared tunnel route dns <tunnel-name> <hostname>
```

This creates a proxied CNAME `<hostname>` → `<uuid>.cfargotunnel.com` in your CF DNS zone.

| Flag | Effect |
|---|---|
| (none) | Fails with `1003` if any record exists at that hostname — safety rail |
| `-f` / `--overwrite-dns` | Replaces whatever's there with the new CNAME — useful but dangerous |

> **Mixed-use domain warning.** If your zone has non-tunnel records (e.g. `mail.kempenich.dev` → Fastmail CNAME), `-f` will silently nuke them if you accidentally list that hostname in your tunnel ingress. Use `-f` deliberately, not as a default. See `.chezmoiscripts/Z--AFTER/run_onchange_after_0030-CLOUDFLARED-sync-themac-routes.sh.tmpl` for the chezmoi script that auto-syncs TheMac routes from YAML.

**Dashboard-managed tunnels:** routes are added via the Zero Trust UI (Tunnels → your tunnel → Public Hostname → Add). The CLI `route dns` command works for these too, but the UI is usually faster.

---

## Recreating a tunnel safely (the dance)

You did this for TheMac. Step-by-step:

1. **Delete old tunnel** (cleans up connector + the dashboard entry):
   ```bash
   cloudflared tunnel delete TheMac
   ```
   Fails if connectors still active — kill the running `cloudflared` process first, or pass `--force`.

2. **Create new tunnel** (new UUID + new credentials JSON):
   ```bash
   cloudflared tunnel create TheMac
   ```
   Writes `~/.cloudflared/<new-uuid>.json`. Old `.json` still sits in the directory — delete manually.

3. **Update config**: change `tunnel:` and `credentials-file:` in your `config-themac.yml` to the new UUID.

4. **Re-route DNS for each hostname**:
   ```bash
   cloudflared tunnel route dns TheMac sketchpad.kempenich.dev
   cloudflared tunnel route dns TheMac outpost.kempenich.dev
   # ...
   ```
   Stale CNAMEs from the old tunnel will fail with `1003` — use `-f` once per hostname after verifying it's just the stale tunnel CNAME.

5. **Start the new connector**:
   ```bash
   cloudflared tunnel --config ~/.cloudflared/config-themac.yml run TheMac
   ```

> **For TheMac specifically:** chezmoi has you covered. Edit `private_dot_cloudflared/config-themac.yml.tmpl` with the new UUID, run `chezmoi apply` — the `0030-CLOUDFLARED-sync-themac-routes.sh` script auto-runs `route dns -f` for every ingress hostname. Only manual step is the `tunnel create` + updating the UUID in the template.

---

## Autostart on macOS (not currently set up on TheMac)

Right now you run `cloudflared tunnel run TheMac` manually each session. Two ways to make it survive reboots:

### Option A: `cloudflared service install` (recommended)

```bash
sudo cloudflared service install                  # creates LaunchDaemon
sudo launchctl start com.cloudflare.cloudflared   # start now
sudo launchctl stop com.cloudflare.cloudflared    # stop without uninstalling
```

Reads `/Library/Cloudflared/config.yml` (or `~/.cloudflared/config.yml` if symlinked there). Logs to `/Library/Logs/com.cloudflare.cloudflared/`.

Uninstall: `sudo cloudflared service uninstall`.

### Option B: brew services

```bash
brew services start cloudflared
```

Simpler but you have less control over the launchd plist. Fine for "I just want it running."

> **Pick one.** Don't run service-install AND `brew services start` AND manual `tunnel run` — three connectors will compete for the same tunnel UUID. Not catastrophic (CF tolerates it) but noisy in logs and wasteful.

---

## Multi-connector / HA

Same tunnel can run from multiple connectors simultaneously. CF load-balances inbound requests across all healthy connectors. Failover is automatic.

**Setup:** copy `<uuid>.json` to each machine, run `cloudflared tunnel run TheMac` on each. That's it. Each one registers as a connector on the same tunnel.

**Real use cases for you:**

- **TheMac on laptop AND old Mac mini as backup**: laptop closes → mini keeps tunnel up
- **TheHome - K8S spread across multiple cluster nodes**: K8s deployment with `replicas: 2+` already gives you this for free via the helm chart
- **Geographic redundancy**: one connector at home, one on a DigitalOcean droplet — survives home internet outages for hostnames whose origin lives on the droplet

**Watchouts:**
- All connectors must reach the same origin services. If `localhost:8000` only exists on TheMac, putting a second connector on a NAS that lacks that service → some requests 502 randomly.
- Credentials JSON is shared across all connectors — treat it like a fleet-wide secret.

---

## Cloudflare Access (you don't use this — should consider)

Zero Trust auth layer that gates who can hit a tunneled hostname. **Without Access:** anyone with the URL hits your service. **With Access:** CF requires login (Google, GitHub, email OTP, etc.) before forwarding the request. Your service sees only authenticated traffic.

No code change in the service. Auth happens at CF's edge.

**Setup (high level):**
1. Zero Trust dashboard → Access → Applications → Add a self-hosted app
2. Application domain: `sketchpad.kempenich.dev`
3. Identity provider: One-Time PIN (email — zero config) or Google
4. Policy: `Include — Emails — flo@kempenich.ai`
5. Save. Next request to that hostname prompts for login first.

**Bonus for personal hostnames:** with One-Time PIN, anyone you whitelist by email gets in via a 6-digit code mailed to them. No accounts to manage. Perfect for "I want my partner to access the family dashboard but not the rest of the internet."

**Pairs powerfully with tunnels:** the combination = "host anything internal, expose to internet, but only logged-in me can reach it." Replaces most VPN use cases for HTTP services.

> **Caveat:** Access policies apply to the hostname, not the tunnel. If you have `internal.kempenich.dev` and `public.kempenich.dev` on the same tunnel, only the one with the Access app gets gated.

---

## Non-HTTP origins (you don't use this — could replace some Tailscale SSH)

Tunnels can carry SSH, raw TCP, even RDP — not just HTTP. Combined with Access, you get browser-auth'd SSH into any machine without exposing port 22 or running a VPN.

**Origin side** — add to ingress:
```yaml
- hostname: ssh.kempenich.dev
  service: ssh://localhost:22
```

**Client side** — install `cloudflared` locally, then:
```bash
ssh -o ProxyCommand="cloudflared access ssh --hostname %h" user@ssh.kempenich.dev
```

Or add to `~/.ssh/config`:
```
Host ssh.kempenich.dev
  ProxyCommand cloudflared access ssh --hostname %h
```

If the hostname is behind Access, `cloudflared access ssh` opens a browser, you log in, the connection proceeds. No public SSH port. Auth via Google/email — way easier than juggling SSH keys.

> **vs Tailscale.** Tailscale gives you a private network (any port, any protocol, peer-to-peer). CF Access+Tunnel gives you internet-exposed services with browser auth. Different tools — but for "SSH into TheMac from any browser I happen to be at" Access is friction-free where Tailscale needs the client installed.

---

## Debugging

| Symptom | Where to look |
|---|---|
| Tunnel won't start | `cloudflared` stderr (usually a YAML syntax error or missing credentials file) |
| `error 1033` in browser | Tunnel is down or no connector registered. `cloudflared tunnel info <name>` |
| `error 1016` (DNS resolution) | CNAME for hostname missing or wrong. `dig HOSTNAME CNAME` (won't show through proxy — use CF dashboard) |
| `error 502` from origin | Tunnel up, origin service down. `curl http://localhost:PORT` directly on the host |
| `error 521` "web server is down" | Origin refused connection. Same fix as 502. |
| Routes silently disappearing | Another tunnel/script is overwriting them with `-f`. Check what else manages routes on that domain. |
| Logs (service-mode macOS) | `/Library/Logs/com.cloudflare.cloudflared/cloudflared.log` |
| Logs (manual run) | stderr of the process |

`cloudflared tunnel info <name>` is the workhorse — shows live connectors, their datacenters, last-seen timestamps. If it shows zero connectors, no `cloudflared` is running for that tunnel.

---

## Quick reference

### Daily commands

```bash
cloudflared tunnel list                                  # what tunnels exist
cloudflared tunnel info <name>                           # is it healthy
cloudflared tunnel run <name>                            # start a connector
cloudflared tunnel route dns <name> <hostname>           # add DNS route
cloudflared tunnel route dns -f <name> <hostname>        # ...overwrite existing record
```

### Lifecycle

```bash
cloudflared tunnel login                                 # once per account
cloudflared tunnel create <name>                         # new tunnel
cloudflared tunnel delete <name>                         # remove
```

### Service mode (macOS)

```bash
sudo cloudflared service install                         # install LaunchDaemon
sudo launchctl start com.cloudflare.cloudflared          # start
sudo launchctl stop com.cloudflare.cloudflared           # stop
sudo cloudflared service uninstall                       # remove
```

### Files in `~/.cloudflared/`

| File | What |
|---|---|
| `cert.pem` | Account-level auth (admin) |
| `<uuid>.json` | Per-tunnel credentials (runtime) |
| `config.yml` | Default config (symlink to per-tunnel config recommended) |
| `config-<name>.yml` | Per-tunnel YAML (Flo's pattern: one file per tunnel, `config.yml` symlinks to active one) |

### Decision guide

| I want to... | Use |
|---|---|
| Expose a local dev port to the internet | CLI mode + local YAML |
| Run a permanent service on a NAS/server | Dashboard-managed |
| Run inside HAOS or K8s | Embedded (add-on / helm chart) |
| Require login before anyone hits the service | Add Cloudflare Access app to the hostname |
| SSH to a machine without public port 22 | Non-HTTP ingress (`ssh://...`) + `cloudflared access ssh` client |
| Make tunnel survive reboot (macOS) | `sudo cloudflared service install` |
| Add redundancy (no single point of failure) | Run same tunnel on N machines (multi-connector) |
| Sync DNS routes from YAML automatically | The chezmoi script: `Z--AFTER/0030-CLOUDFLARED-sync-themac-routes.sh.tmpl` |
