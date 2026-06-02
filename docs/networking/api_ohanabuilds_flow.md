# api.ohanabuilds.org Flow

Metadata:
- Purpose: Document current request routing for `https://api.ohanabuilds.org`.
- Phase: Cloud gateway discovery and G2 boundary audit.
- Last updated: 2026-06-02.
- Source: Read-only SSH inspection of `georgeCloud`.

## Current Request Flow

```text
Internet client
  |
  v
https://api.ohanabuilds.org
  |
  v
nginx on GeorgeDroplet :443
  |
  v
proxy_pass http://127.0.0.1:3000
  |
  v
PM2 app: george-cloud-api
  |
  v
Express routes in /home/jacque/george-cloud-api/server.js
  |
  v
for POST /api/ingest only:
Bearer token check
  |
  v
forward JSON body to MINIMAC_INGEST_URL over Tailscale
```

## Public Host

Domain:

```text
api.ohanabuilds.org
```

Cloud host:

```text
GeorgeDroplet
```

## Nginx Site

Active nginx site:

```text
/etc/nginx/sites-available/george-cloud-api
/etc/nginx/sites-enabled/george-cloud-api
```

HTTPS server block:

- `server_name api.ohanabuilds.org`
- `listen 443 ssl`
- Certbot-managed certificate
- `location /` proxies to `http://127.0.0.1:3000`
- `location = /api/ingest` also proxies to `http://127.0.0.1:3000`
- `/api/ingest` applies nginx rate limiting

HTTP server block:

- redirects matching host to HTTPS
- includes `/api/ingest` proxy stanza
- has Certbot-managed `return 404` fallback

## Rate Limiting

Nginx config:

```text
/etc/nginx/conf.d/george-cloud-api-rate-limit.conf
```

Observed rule:

```text
rate=30r/m
burst=10 nodelay
```

This applies to:

```text
location = /api/ingest
```

## TLS

Certificate source:

```text
Certbot / Let's Encrypt
```

Relevant files:

```text
/etc/letsencrypt/live/api.ohanabuilds.org/fullchain.pem
/etc/letsencrypt/live/api.ohanabuilds.org/privkey.pem
/etc/letsencrypt/renewal/api.ohanabuilds.org.conf
```

Renewal:

```text
certbot.timer enabled and active
```

## Local App

PM2 app:

```text
george-cloud-api
```

Script:

```text
/home/jacque/george-cloud-api/server.js
```

Bind:

```text
127.0.0.1:3000
```

Startup:

```text
pm2-jacque.service -> pm2 resurrect
```

## Routes

Observed routes from `server.js`:

| Method | Path | Behavior |
| --- | --- | --- |
| `GET` | `/health` | returns healthy JSON |
| `POST` | `/api/ingest` | requires bearer token, forwards JSON to MiniMac URL |
| any | `/` | no explicit route; Express returns 404 |

## Ingest Auth

`POST /api/ingest` expects:

```text
Authorization: Bearer <token>
```

Expected token comes from:

```text
GEORGE_API_TOKEN
```

The token value was not documented.

## Forwarding Target

Forward target comes from:

```text
MINIMAC_INGEST_URL
```

Existing cloud README describes the intended target as:

```text
http://100.120.201.45:3032/api/cloud-ingest
```

That is a Tailscale address for MiniMac. At inspection time the MiniMac node was
listed as offline in `tailscale status`, so successful forwarding likely depends
on that device being online.

## Failure Behavior

Observed in `server.js`:

- missing `Authorization` header returns `401`
- invalid token returns `403`
- missing MiniMac URL returns `502`
- MiniMac forward failure returns `502`
- payload too large returns `413`
- successful forward returns `202`

## Boundary Observation

The current cloud route acts as:

- public HTTPS entrypoint
- rate limiter
- token authenticator
- forwarder to a Tailscale node

It does not appear to own domain analytics directly. That boundary aligns with
the George 3 direction, but the implementation is still George 2-era and should
not be copied wholesale.

