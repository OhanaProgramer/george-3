# George 2 Boundary Audit

Metadata:
- Purpose: Identify what existing George 2 cloud infrastructure exists and how it should be treated.
- Phase: Cloud gateway discovery and G2 boundary audit.
- Last updated: 2026-06-02.
- Source: Read-only SSH inspection of `georgeCloud`.

## Executive Summary

The inspected George 2 cloud footprint is compact:

- one nginx virtual host for `api.ohanabuilds.org`
- one PM2-managed Node app, `george-cloud-api`
- one token-protected ingest route
- one Tailscale forwarding target to MiniMac

This is useful as a networking/auth reference, but George 3 should not recreate
the George 2 structure. George 3 should keep data, analytics, coaching, and
reports on George hosts and use cloud only as a lightweight authenticated
gateway.

## Existing George 2 Components

### Cloud Gateway Repo

Path:

```text
/home/jacque/george-cloud-api
```

Purpose:

- Express app
- health endpoint
- protected ingest endpoint
- bearer token validation
- forwards accepted payloads to MiniMac over Tailscale

Runtime:

- Node `24.15.0`
- PM2 app `george-cloud-api`
- localhost bind `127.0.0.1:3000`

### Reverse Proxy

Path:

```text
/etc/nginx/sites-available/george-cloud-api
```

Purpose:

- public HTTPS for `api.ohanabuilds.org`
- proxy to local Node app
- Certbot-managed TLS
- rate limit `/api/ingest`

### Token Auth

Environment key:

```text
GEORGE_API_TOKEN
```

Pattern:

- client sends bearer token
- cloud compares against env token
- missing token returns `401`
- wrong token returns `403`

Secret value was intentionally not documented.

### Forwarding Logic

Environment key:

```text
MINIMAC_INGEST_URL
```

Pattern:

- cloud receives authenticated JSON
- cloud forwards JSON body to MiniMac over Tailscale
- cloud returns `202` only if the downstream accepts
- downstream failure returns safe `502`

Existing README identifies the target as:

```text
http://100.120.201.45:3032/api/cloud-ingest
```

### Tailscale

Tailscale is active on `GeorgeDroplet`.

Observed nodes:

- `georgedroplet`: online
- `macbook`: online
- `minimac`: offline at inspection

This confirms George 2 already relies on Tailscale as a private forwarding
network.

## Useful Patterns For George 3

These patterns are worth preserving conceptually:

- Cloud terminates public HTTPS.
- Cloud performs simple token authentication.
- Cloud rate limits public endpoints before app code.
- Cloud forwards to a George host over Tailscale.
- Cloud app binds only to localhost behind nginx.
- Gateway logs request method/path/status/duration without request bodies.
- Domain logic stays off the cloud gateway.
- Environment variables define port, token, and downstream URL.
- PM2 plus systemd provides simple service persistence.

## Patterns Not To Copy Wholesale

George 3 should avoid carrying forward these George 2 traits:

- cloud gateway as a general app surface
- cloud-owned domain data
- cloud-owned analytics
- cloud-owned coaching logic
- device-specific naming embedded in gateway design, such as MiniMac-specific URLs
- one-off route growth without clear domain/interface separation
- secrets appearing in PM2 saved process dumps

## Potential Future Retirement Candidates

Do not remove these yet. They are candidates for later review only.

| Candidate | Why It May Retire |
| --- | --- |
| `george-cloud-api` as currently implemented | Replace with a George 3 lightweight gateway when G3 remote ingress is ready |
| MiniMac-specific forwarding target | G3 should route to a configured George host, not a hard-coded historical receiver |
| `/api/cloud-ingest` downstream route on MiniMac | May be replaced by a G3 host-owned interface/API |
| PM2 saved secret environment | Token value appears persisted in PM2 state; future cleanup should avoid secret duplication |
| default nginx site in `sites-available/default` | Not enabled, but can remain as package reference until cleanup |
| public `/api/ingest` G2 route | May be replaced by G3-specific route naming and auth contract |

## Not Observed

During this audit, these were not observed on `georgeCloud`:

- Caddy
- Cloudflare tunnel / `cloudflared`
- multiple active George app repos
- Python API servers such as Gunicorn or Uvicorn
- dashboard services
- pushup analytics running on the cloud host
- active public listeners beyond SSH, HTTP, HTTPS, DNS stubs, Tailscale, and the localhost Node app

## Boundary Recommendation

Treat G2 as a reference, not a template.

Reusable:

- token gate
- nginx TLS and rate limit
- Tailscale forwarding
- localhost-bound app behind reverse proxy

Do not preserve:

- historical MiniMac assumptions
- any cloud ownership of George domain behavior
- ad hoc route expansion

