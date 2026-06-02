# George 3 Cloud Gateway Plan

Metadata:
- Purpose: Define the clean target architecture for George 3 cloud ingress.
- Phase: Cloud gateway discovery and G2 boundary audit.
- Last updated: 2026-06-02.
- Status: Planning only; no production infrastructure changed.

## Target Architecture

```text
Internet
  |
  v
api.ohanabuilds.org
  |
  v
Lightweight authenticated cloud gateway
  |
  v
Tailscale
  |
  v
George 3 host
  |
  v
domains/pushups
domains/running
domains/finance
future domains
```

## Core Principle

Cloud should be a controlled gateway, not George's brain.

Cloud owns:

- TLS/public ingress
- authentication
- request validation
- rate limiting
- forwarding
- minimal gateway logs

George host owns:

- data
- analytics
- coaching
- reports
- domain rules
- local interfaces
- write behavior

## Desired Cloud Responsibilities

### Public HTTPS

Keep:

- `api.ohanabuilds.org`
- nginx or equivalent TLS termination
- Certbot or equivalent automated certificate renewal

### Authentication

Use a simple gateway auth contract initially:

- bearer token or signed request
- token lives in cloud environment
- no token values in docs or git
- missing token returns `401`
- invalid token returns `403`

Future options can include short-lived tokens or signed payloads, but do not
build that until the basic G3 route is needed.

### Rate Limiting

Retain nginx-level rate limiting for public endpoints. The existing G2 pattern
of limiting ingest routes before app code is useful.

### Forwarding

Forward authenticated requests over Tailscale only.

The forwarding target should be configuration-driven:

```text
GEORGE3_FORWARD_BASE_URL=http://<tailscale-ip-or-magicdns>:<port>
```

Avoid hard-coding historical host names or MiniMac-specific assumptions in the
gateway implementation.

### Logging

Gateway logs should include:

- method
- path
- status
- duration
- request id if added

Gateway logs should not include:

- request bodies
- bearer tokens
- domain data payloads beyond coarse metadata

## What Cloud Must Not Own

Cloud must not own:

- pushup data
- running data
- finance data
- analytics
- coaching language
- reports
- dashboard state
- domain migrations
- LLM orchestration
- voice behavior

## George 3 Host Responsibilities

The George 3 host should receive forwarded requests through a local interface,
then hand off to domains:

```text
interfaces/api or interfaces/web
  |
  v
domains/pushups/service.py
domains/pushups/analytics.py
domains/pushups/advisor.py
```

For Pushups specifically:

- `domains/pushups/data/events.ndjson` remains the authoritative local dataset.
- `domains/pushups/service.py` owns append behavior.
- `domains/pushups/analytics.py` owns calculations.
- cloud never calculates pushup coaching metrics.

## Recommended Migration Sequence

1. Leave current G2 gateway untouched.
2. Define a G3 ingress contract locally in George 3.
3. Add a local G3 API/interface endpoint on the George host.
4. Test over localhost.
5. Test over Tailscale from `georgeCloud` to the George host.
6. Add a new cloud route that forwards to the G3 endpoint.
7. Run G2 and G3 routes in parallel.
8. Confirm G3 route behavior and logging.
9. Only then mark G2 routes as retirement candidates.

Every step should be independently testable and reversible.

## Initial G3 Route Shape

Potential future route:

```text
POST /g3/pushups/events
```

Cloud behavior:

- authenticate
- rate limit
- forward unchanged JSON over Tailscale

George host behavior:

- validate reps
- append event
- return structured result

This route is only a planning example. Do not build it until explicitly
requested.

## Security Notes

- Do not bind George host services to public interfaces.
- Prefer Tailscale IP or MagicDNS for cloud-to-host forwarding.
- Do not expose local Pushups Entry directly to the public internet.
- Do not forward unauthenticated public traffic into the tailnet.
- Avoid storing secrets in process manager dumps when possible.
- Keep cloud payload limits small.

## Survival List

Patterns that should survive into George 3:

- Tailscale-first private forwarding
- localhost-bound gateway behind nginx
- Certbot-managed TLS
- public route rate limiting
- bearer-token gate as a starting point
- clean request logging
- domain logic on George host

## Retirement List

Components to consider retiring later:

- G2 MiniMac-specific ingest route
- G2 cloud app once G3 gateway is live
- any cloud-side domain logic if discovered later
- any route that forwards without a clear G3 domain/interface contract

No retirement should happen during this audit phase.

