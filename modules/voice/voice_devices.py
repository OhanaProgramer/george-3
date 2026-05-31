"""Read-only voice/audio discovery for George 3."""

from __future__ import annotations

import json
import subprocess

from config import settings


def run_command(command, timeout_seconds=5):
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )


def discover_voice_devices(command_runner=run_command):
    microphones, speakers = discover_audio_devices(command_runner)
    apple_voices = discover_apple_voices(command_runner)

    configured_voice = settings.VOICE_NAME
    configured_voice_found = None

    if configured_voice:
        configured_voice_found = has_name_match(apple_voices, configured_voice)

    return {
        "voice_engine": settings.VOICE_ENGINE,
        "configured_voice": configured_voice,
        "configured_voice_found": configured_voice_found,
        "input_device_hint": settings.VOICE_INPUT_DEVICE_HINT,
        "input_target_found": has_name_match(microphones, settings.VOICE_INPUT_DEVICE_HINT),
        "output_device_hint": settings.VOICE_OUTPUT_DEVICE_HINT,
        "output_target_found": output_target_found(
            speakers,
            settings.VOICE_OUTPUT_DEVICE_HINT,
            settings.VOICE_PRODUCTION_SPEAKER_HINT,
        ),
        "production_speaker_hint": settings.VOICE_PRODUCTION_SPEAKER_HINT,
        "microphones": microphones,
        "speakers": speakers,
        "apple_voices": apple_voices,
    }


def discover_audio_devices(command_runner=run_command):
    result = command_runner(["system_profiler", "SPAudioDataType", "-json"])

    if result.returncode != 0:
        return [], []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return [], []

    devices = []
    for section in data.get("SPAudioDataType", []):
        devices.extend(section.get("_items", []))

    microphones = []
    speakers = []

    for device in devices:
        normalized = normalize_audio_device(device)

        if normalized["input_channels"] > 0:
            microphones.append(normalized)

        if normalized["output_channels"] > 0 or normalized["is_default_system_output"]:
            speakers.append(normalized)

    return microphones, speakers


def normalize_audio_device(device):
    return {
        "name": device.get("_name", "unknown"),
        "manufacturer": device.get("coreaudio_device_manufacturer", ""),
        "transport": device.get("coreaudio_device_transport", ""),
        "sample_rate": device.get("coreaudio_device_srate"),
        "input_channels": int(device.get("coreaudio_device_input", 0) or 0),
        "output_channels": int(device.get("coreaudio_device_output", 0) or 0),
        "is_default_input": device.get("coreaudio_default_audio_input_device") == "spaudio_yes",
        "is_default_output": device.get("coreaudio_default_audio_output_device") == "spaudio_yes",
        "is_default_system_output": device.get("coreaudio_default_audio_system_device") == "spaudio_yes",
    }


def discover_apple_voices(command_runner=run_command):
    result = command_runner(["say", "-v", "?"])

    if result.returncode != 0:
        return []

    return [voice for voice in (parse_apple_voice_line(line) for line in result.stdout.splitlines()) if voice]


def parse_apple_voice_line(line):
    if not line.strip():
        return None

    before_comment = line.split("#", 1)[0].rstrip()
    parts = before_comment.rsplit(None, 1)

    if len(parts) != 2:
        return None

    name, locale = parts
    return {"name": name.strip(), "locale": locale.strip()}


def has_name_match(items, hint):
    if not hint:
        return False

    normalized_hint = hint.lower()
    return any(normalized_hint in item.get("name", "").lower() for item in items)


def output_target_found(speakers, output_hint, production_hint):
    if output_hint == "system_default":
        return any(speaker["is_default_system_output"] or speaker["is_default_output"] for speaker in speakers)

    if output_hint:
        return has_name_match(speakers, output_hint)

    if production_hint:
        return has_name_match(speakers, production_hint)

    return False


def format_voice_summary(discovery):
    lines = [
        "George 3 Voice Discovery",
        f"Voice engine: {discovery['voice_engine']}",
        f"Configured voice: {discovery['configured_voice'] or 'not set'}",
        f"Configured voice found: {format_optional_bool(discovery['configured_voice_found'])}",
        f"Input hint: {discovery['input_device_hint']}",
        f"Input target found: {'yes' if discovery['input_target_found'] else 'no'}",
        f"Output hint: {discovery['output_device_hint']}",
        f"Output target found: {'yes' if discovery['output_target_found'] else 'no'}",
        f"Microphones: {len(discovery['microphones'])}",
        f"Speakers: {len(discovery['speakers'])}",
        f"Apple voices: {len(discovery['apple_voices'])}",
    ]
    return "\n".join(lines)


def format_optional_bool(value):
    if value is None:
        return "not checked"
    return "yes" if value else "no"


def main():
    print(format_voice_summary(discover_voice_devices()))


if __name__ == "__main__":
    main()
