# Readiness Module Contract

This module answers:

```text
Is this George node ready to operate?
```

## Allowed in v1

- call existing module status functions
- summarize system readiness
- summarize Tailscale readiness
- summarize voice readiness
- combine statuses into one structured object
- print a clean terminal summary

## Not Allowed in v1

- dashboard UI
- API routing
- remote control
- service restart
- auto-repair
- cloud forwarding
- authentication

The readiness module is a reader and summarizer only. It does not fix, restart,
or mutate anything.

Readiness is operational status only. It is not related to fitness, medical,
biometric, sleep, or wellness data.
