# Current Cloud Inventory

Metadata:
- Purpose: Inventory active George cloud infrastructure behind `api.ohanabuilds.org`.
- Phase: Cloud gateway discovery and G2 boundary audit.
- Last updated: 2026-06-02.
- Source: Read-only SSH inspection of `georgeCloud`.
- Safety: No production files were modified, deleted, restarted, or reloaded.

## Host

- SSH alias: `georgeCloud`
- Hostname: `GeorgeDroplet`
- User inspected as: `jacque`
- OS/kernel: Ubuntu Linux, kernel `6.8.0-117-generic`
- Public role observed: HTTPS reverse proxy and lightweight George cloud gateway.

## Active Services

| Service | Status | Purpose | Startup |
| --- | --- | --- | --- |
| `nginx.service` | running | Public HTTP/HTTPS reverse proxy for `api.ohanabuilds.org` | systemd |
| `pm2-jacque.service` | running | Resurrects PM2 apps for user `jacque` | systemd |
| `tailscaled.service` | running | Tailscale node agent | systemd |
| `ssh.service` | running | SSH access | systemd |
| `fail2ban.service` | running | SSH/service abuse protection | systemd |
| `do-agent.service` | running | DigitalOcean monitoring agent | systemd |
| `droplet-agent.service` | running | DigitalOcean droplet agent | systemd |
| `cron.service` | running | Scheduled tasks | systemd |
| `certbot.timer` | enabled/active | Certificate renewal timer | systemd timer |

Other normal system services were active, including journald, logind, resolved,
networkd, timesyncd, udev, unattended-upgrades, and user session services.

## Listening Ports

| Address | Port | Observed Purpose |
| --- | ---: | --- |
| `0.0.0.0` | `80` | nginx HTTP listener |
| `0.0.0.0` | `443` | nginx HTTPS listener |
| `0.0.0.0` / `[::]` | `22` | SSH |
| `127.0.0.1` | `3000` | Node app `george-cloud-api` |
| `0.0.0.0` / `[::]` UDP | `41641` | Tailscale WireGuard |
| `100.86.212.103` | `65520` | Tailscale-related listener |
| `fd7a:115c:a1e0::e601:d4af` | `36167` | Tailscale-related IPv6 listener |
| `127.0.0.53`, `127.0.0.54` | `53` | systemd-resolved DNS |

## PM2 Apps

| Name | Status | Path | Port | Runtime | Notes |
| --- | --- | --- | ---: | --- | --- |
| `george-cloud-api` | online | `/home/jacque/george-cloud-api/server.js` | `3000` | Node `24.15.0` | PM2 fork mode, 5 restarts, uptime about 5 days at inspection |

PM2 startup is provided by:

```text
/etc/systemd/system/pm2-jacque.service
```

The PM2 app logs are:

```text
/home/jacque/.pm2/logs/george-cloud-api-out.log
/home/jacque/.pm2/logs/george-cloud-api-error.log
```

## Cloud App Directory

Observed app directory:

```text
/home/jacque/george-cloud-api
```

Important files:

| File | Purpose |
| --- | --- |
| `server.js` | Express gateway with health and ingest routes |
| `package.json` | Node package metadata and dependencies |
| `.env` | Local project env file; contains secrets and should not be copied |
| `README.md` | Existing cloud gateway notes |
| `node_modules/` | Installed Node dependencies |

Dependencies observed in `package.json`:

- `express`
- `dotenv`

## Environment Keys

The cloud app loads:

```text
/etc/george-cloud-api.env
```

Observed key names only:

- `GEORGE_API_TOKEN`
- `PORT`
- `MINIMAC_INGEST_URL`

Secret values were intentionally not documented.

## Tailscale

Observed `tailscale status`:

| Tailscale IP | Node | Status |
| --- | --- | --- |
| `100.86.212.103` | `georgedroplet` | online |
| `100.121.228.7` | `macbook` | online |
| `100.120.201.45` | `minimac` | offline, last seen 4 days before inspection |

This confirms Tailscale is already part of the cloud forwarding pattern.

## Nginx

Nginx version:

```text
nginx/1.24.0 (Ubuntu)
```

Enabled site:

```text
/etc/nginx/sites-enabled/george-cloud-api
  -> /etc/nginx/sites-available/george-cloud-api
```

Rate limit config:

```text
/etc/nginx/conf.d/george-cloud-api-rate-limit.conf
```

Rate limit observed:

```text
limit_req_zone $binary_remote_addr zone=george_ingest_limit:10m rate=30r/m;
```

Caddy was not installed or active.

## TLS

TLS for `api.ohanabuilds.org` is managed by Certbot.

Observed certificate references:

```text
/etc/letsencrypt/live/api.ohanabuilds.org/fullchain.pem
/etc/letsencrypt/live/api.ohanabuilds.org/privkey.pem
/etc/letsencrypt/options-ssl-nginx.conf
/etc/letsencrypt/ssl-dhparams.pem
```

Certbot timer was enabled and active.

## Health Check

Local app health check:

```text
GET http://127.0.0.1:3000/health
```

Returned:

```json
{"ok":true,"service":"george-cloud-api","status":"healthy"}
```

Root path:

```text
GET http://127.0.0.1:3000/
```

Returned `404` with Express `Cannot GET /`.

## Inventory Summary

Current cloud is small:

- nginx terminates HTTPS and proxies to localhost
- PM2 runs one Node Express app
- Express authenticates `/api/ingest`
- Express forwards accepted payloads to MiniMac over Tailscale
- cloud does not appear to own pushup analytics or reports

