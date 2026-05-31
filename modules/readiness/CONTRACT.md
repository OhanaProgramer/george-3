# Readiness Module Contract

Metadata:
- Purpose: Define readiness module boundaries.
- Phase: Voice Speak Readiness v1.
- Last updated: 2026-05-31.
- Notes: Operational readiness only; not human health; no audio playback.

This module answers:

```text
Is this George node ready to operate?
```

## Allowed in v1

- call existing module status functions
- summarize system readiness
- summarize Tailscale readiness
- summarize voice discovery readiness
- summarize voice speak configuration readiness without speaking aloud
- combine statuses into one structured object
- print a clean terminal summary

## Inputs

- system status object
- Tailscale status object
- voice discovery object

## Outputs

- structured readiness object
- terminal summary for humans

## Not Allowed in v1

- dashboard UI
- API routing
- remote control
- service restart
- auto-repair
- cloud forwarding
- authentication
- recording
- transcription
- wake word detection
- AI calls
- audio playback during readiness checks

The readiness module is a reader and summarizer only. It does not fix, restart,
mutate anything, call `say`, or call `speak_text()`.

Readiness is operational status only. It is not related to fitness, medical,
biometric, sleep, or wellness data.
