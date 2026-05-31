"""Readiness status aggregation.

Purpose: Summarize whether this George node is ready to operate.
Phase: Readiness Aggregator v1.
Last updated: 2026-05-31.
Notes: Reader/summarizer only; does not repair or mutate system state.
"""

from __future__ import annotations

from datetime import datetime, timezone

from modules.system.system_status import get_system_status
from modules.tailscale.tailscale_status import get_tailscale_status
from modules.voice.voice_devices import discover_voice_devices


STATUS_ORDER = {"ok": 0, "warning": 1, "error": 2}


def get_readiness_status(
    system_reader=get_system_status,
    tailscale_reader=get_tailscale_status,
    voice_reader=discover_voice_devices,
    timestamp_reader=None,
):
    timestamp_reader = timestamp_reader or utc_timestamp
    details = {
        "system": safe_read(system_reader),
        "tailscale": safe_read(tailscale_reader),
        "voice": safe_read(voice_reader),
    }

    checks = {
        "system": evaluate_system(details["system"]),
        "tailscale": evaluate_tailscale(details["tailscale"]),
        "voice": evaluate_voice(details["voice"]),
    }

    return {
        "overall_status": combine_statuses(check["status"] for check in checks.values()),
        "checks": checks,
        "details": details,
        "timestamp": timestamp_reader(),
    }


def safe_read(reader):
    try:
        return reader()
    except Exception as error:
        return {
            "module_error": True,
            "error": str(error),
        }


def evaluate_system(system_status):
    if system_status.get("module_error"):
        return check("error", f"System module failed: {system_status['error']}")

    node = system_status.get("node") or {}
    host = system_status.get("host") or {}
    resources = system_status.get("resources") or {}
    missing_core = []

    for label, value in {
        "node.name": node.get("name"),
        "node.role": node.get("role"),
        "node.environment": node.get("environment"),
        "host.hostname": host.get("hostname"),
        "host.os": host.get("os"),
        "host.python_version": host.get("python_version"),
    }.items():
        if not value:
            missing_core.append(label)

    if missing_core:
        return check("error", f"System missing core fields: {', '.join(missing_core)}")

    optional_missing = [
        name
        for name in ("memory_total_gb", "disk_total_gb", "disk_free_gb")
        if resources.get(name) is None
    ]

    if optional_missing:
        return check("warning", f"System optional data missing: {', '.join(optional_missing)}")

    return check("ok", "System core data is present.")


def evaluate_tailscale(tailscale_status):
    if tailscale_status.get("module_error"):
        return check("error", f"Tailscale module failed: {tailscale_status['error']}")

    if tailscale_status.get("backend_state") == "Running" and tailscale_status.get("tailscale_ip"):
        return check("ok", "Tailscale is running with a local IP.")

    if not tailscale_status.get("installed"):
        return check("error", "Tailscale is not installed.")

    if tailscale_status.get("backend_state") != "Running":
        return check("error", f"Tailscale backend state is {tailscale_status.get('backend_state', 'unknown')}.")

    return check("error", "Tailscale local IP is missing.")


def evaluate_voice(voice_status):
    if voice_status.get("module_error"):
        return check("error", f"Voice module failed: {voice_status['error']}")

    devices_check = evaluate_voice_devices(voice_status)
    speak_config_check = evaluate_voice_speak_config(voice_status)
    status = combine_statuses((devices_check["status"], speak_config_check["status"]))

    if status != "ok":
        summary = "; ".join(
            subcheck["summary"]
            for subcheck in (devices_check, speak_config_check)
            if subcheck["status"] == status
        )
    else:
        summary = "Voice discovery and speak config are ready."

    return {
        "status": status,
        "summary": summary,
        "devices": devices_check,
        "speak_config": speak_config_check,
    }


def evaluate_voice_devices(voice_status):
    if not voice_status.get("input_target_found"):
        return check("error", "Voice input target was not found.")

    if not voice_status.get("output_target_found"):
        return check("error", "Voice output target was not found.")

    optional_warnings = []

    if voice_status.get("voice_engine") == "apple" and not voice_status.get("apple_voices"):
        optional_warnings.append("Apple voices not discovered")

    if optional_warnings:
        return check("warning", "; ".join(optional_warnings))

    return check("ok", "Voice input and output targets are available.")


def evaluate_voice_speak_config(voice_status):
    voice_engine = voice_status.get("voice_engine")
    configured_voice = voice_status.get("configured_voice")

    if voice_engine != "apple":
        return check("error", f"Voice engine is not supported for speaking: {voice_engine or 'not set'}.")

    if not configured_voice:
        return check("ok", "Apple speech will use the system default voice.")

    if voice_status.get("configured_voice_found") is True:
        return check("ok", "Configured Apple voice is available.")

    return check("error", "Configured Apple voice was not found.")


def check(status, summary):
    return {
        "status": status,
        "summary": summary,
    }


def combine_statuses(statuses):
    return max(statuses, key=lambda status: STATUS_ORDER[status])


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


def format_readiness_summary(readiness):
    checks = readiness["checks"]
    return "\n".join(
        [
            "George 3 Readiness Status",
            f"Overall: {checks_label(readiness['overall_status'])}",
            "",
            f"System: {checks_label(checks['system']['status'])}",
            f"Tailscale: {checks_label(checks['tailscale']['status'])}",
            f"Voice: {checks_label(checks['voice']['status'])}",
            f"  Devices: {checks_label(checks['voice']['devices']['status'])}",
            f"  Speak config: {checks_label(checks['voice']['speak_config']['status'])}",
        ]
    )


def checks_label(status):
    return status.upper()


def main():
    print(format_readiness_summary(get_readiness_status()))


if __name__ == "__main__":
    main()
