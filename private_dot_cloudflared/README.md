# ~/.cloudflared

Cloudflare Tunnel configs for kempenich.dev.

## Layout

```
config-<tunnel>.yml   Per-tunnel config (ingress rules, credentials path)
config.yml            Symlink to the most-used tunnel config (currently TheMac)
<uuid>.json           Runtime credential restored from 1Password by chezmoi
cert.pem              Regenerable admin credential from `cloudflared tunnel login`
```

TheMac's runtime credential lives in the `Chezmoi` vault item
`Cloudflare Tunnel - TheMac`. Chezmoi reads the Secure Note body through
`op://Chezmoi/Cloudflare Tunnel - TheMac/notesPlain` and writes the JSON as
mode `0400`. Never commit the rendered file.

`cert.pem` is intentionally not backed up. It is not needed to run TheMac.
Run `cloudflared tunnel login` again when account-level tunnel or DNS
administration is required.

## Tunnels

| Name           | Purpose                        | Managed via |
|----------------|--------------------------------|-------------|
| TheMac         | Local dev services (sketchpad) | CLI config  |
| DadHome        | Dad's home network             | Dashboard   |
| TheHome - HAOS | Home Assistant OS               | Dashboard   |
| TheHome - K8S  | Home Kubernetes cluster        | Dashboard   |

Dashboard-managed tunnels have no local config file -- their config lives in the Cloudflare Zero Trust dashboard.

## Adding a new local service to TheMac

1. `cloudflared tunnel route dns "TheMac" themac-<service>.kempenich.dev`
2. Add an ingress entry in `config-themac.yml`
3. On the next normal chezmoi apply, `0030` syncs the route and `0031` restarts
   the service.

## LaunchAgent on TheMac

Chezmoi owns the user LaunchAgent directly:

```text
~/Library/LaunchAgents/com.cloudflare.cloudflared.plist
```

It runs `cloudflared tunnel --no-autoupdate --config ~/.cloudflared/config.yml
run`. Homebrew owns binary updates.

The scripts are deliberately adjacent:

1. `0030-CLOUDFLARED-sync-themac-routes`
2. `0031-CLOUDFLARED-install-service`

When both are scheduled, DNS routes are synced before `0031` reloads the
managed plist and verifies that the connector remains alive. Both scripts are
gated to the `TheMac` universe.

## Fresh Mac

1. Install and sign in to the 1Password desktop app and CLI.
2. Bootstrap Homebrew and chezmoi.
3. Initialise chezmoi as a personal, graphical macOS machine in `TheMac`.
4. Apply chezmoi.

Chezmoi installs `cloudflared`, restores the config and runtime credential,
writes and loads the user LaunchAgent, and syncs DNS routes when `cert.pem` is
available. `cloudflared tunnel login` is optional unless administrative
commands are needed.
