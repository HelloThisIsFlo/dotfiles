# ~/.cloudflared

Cloudflare Tunnel configs for kempenich.dev.

## Layout

```
config-<tunnel>.yml   Per-tunnel config (ingress rules, credentials path)
config.yml            Symlink to the most-used tunnel config (currently TheMac)
<uuid>.json           Tunnel credentials (secret -- do not commit)
cert.pem              Account certificate from `cloudflared tunnel login`
```

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
3. Restart `cloudflared tunnel run`
