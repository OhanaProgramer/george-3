"""Isolated Sonos speaker output test for George."""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable, Sequence


DEFAULT_PHRASE = "George Sonos speaker test successful."
DEFAULT_SONOS_IP = "192.168.0.99"
DEFAULT_SONOS_NAME = "Den"
WAV_FILENAME = "george_sonos_speaker_test.wav"


class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


class QuietThreadingHTTPServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        exc_type, exc, _traceback = sys.exc_info()

        if exc_type in {BrokenPipeError, ConnectionResetError}:
            return

        super().handle_error(request, client_address)


def run_command(command, timeout_seconds=15):
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
    )


def get_sonos_ip() -> str:
    return os.getenv("SONOS_SPEAKER_IP", DEFAULT_SONOS_IP)


def get_sonos_name() -> str:
    return os.getenv("SONOS_SPEAKER_NAME", DEFAULT_SONOS_NAME)


def get_local_ip_for_target(target_ip: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect((target_ip, 1400))
        return sock.getsockname()[0]


def generate_wav(
    phrase: str,
    output_file: Path,
    command_runner: Callable = run_command,
) -> dict:
    command = [
        "say",
        "-o",
        str(output_file),
        "--file-format=WAVE",
        "--data-format=LEI16@44100",
        phrase,
    ]

    try:
        command_result = command_runner(command, timeout_seconds=15)
    except subprocess.TimeoutExpired as exc:
        return {
            "success": False,
            "command": command,
            "output_file": str(output_file),
            "error": f"say timed out after {exc.timeout} seconds.",
        }
    except OSError as exc:
        return {
            "success": False,
            "command": command,
            "output_file": str(output_file),
            "error": str(exc),
        }

    if command_result.returncode != 0:
        return {
            "success": False,
            "command": command,
            "output_file": str(output_file),
            "error": command_result.stderr.strip() or "say failed.",
        }

    return {
        "success": True,
        "command": command,
        "output_file": str(output_file),
        "error": "",
    }


def start_http_server(directory: Path, local_ip: str):
    handler = partial(QuietHTTPRequestHandler, directory=str(directory))
    server = QuietThreadingHTTPServer((local_ip, 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def play_sonos_url(
    sonos_ip: str,
    audio_url: str,
    title: str,
    poll_seconds: int = 6,
    sleeper: Callable[[float], None] = time.sleep,
) -> dict:
    try:
        from soco import SoCo
    except ImportError as exc:
        return {"success": False, "error": str(exc), "polls": []}

    try:
        speaker = SoCo(sonos_ip)
        speaker_name = speaker.player_name
        volume = speaker.volume
        mute = speaker.mute
        speaker.play_uri(audio_url, title=title)
        polls = []

        for second in range(1, poll_seconds + 1):
            sleeper(1)
            transport = speaker.get_current_transport_info()
            track = speaker.get_current_track_info()
            polls.append(
                {
                    "second": second,
                    "state": transport.get("current_transport_state", ""),
                    "position": track.get("position", ""),
                    "duration": track.get("duration", ""),
                }
            )
    except Exception as exc:
        return {"success": False, "error": str(exc), "polls": []}

    heard_playing = any(poll["state"] == "PLAYING" for poll in polls)
    return {
        "success": heard_playing,
        "speaker_name": speaker_name,
        "volume": volume,
        "mute": mute,
        "polls": polls,
        "error": "" if heard_playing else "Sonos did not report PLAYING.",
    }


def run_sonos_speaker_test(
    phrase: str = DEFAULT_PHRASE,
    sonos_ip: str | None = None,
    sonos_name: str | None = None,
    poll_seconds: int = 6,
) -> dict:
    sonos_ip = sonos_ip or get_sonos_ip()
    sonos_name = sonos_name or get_sonos_name()
    result = {
        "success": False,
        "phrase": phrase,
        "sonos_ip": sonos_ip,
        "sonos_name": sonos_name,
        "local_ip": "",
        "audio_url": "",
        "wav": {},
        "playback": {},
        "message": "",
        "error": "",
    }

    with tempfile.TemporaryDirectory(prefix="george_sonos_") as tmpdir:
        tmp_path = Path(tmpdir)
        wav_file = tmp_path / WAV_FILENAME
        wav = generate_wav(phrase, wav_file)
        result["wav"] = wav

        if not wav["success"]:
            result["error"] = wav["error"]
            return result

        try:
            local_ip = get_local_ip_for_target(sonos_ip)
            server, thread = start_http_server(tmp_path, local_ip)
        except OSError as exc:
            result["error"] = str(exc)
            return result

        try:
            port = server.server_address[1]
            audio_url = f"http://{local_ip}:{port}/{WAV_FILENAME}"
            result["local_ip"] = local_ip
            result["audio_url"] = audio_url
            playback = play_sonos_url(
                sonos_ip,
                audio_url,
                title="George Sonos speaker test",
                poll_seconds=poll_seconds,
            )
            result["playback"] = playback
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    if not result["playback"].get("success"):
        result["error"] = result["playback"].get("error") or "Sonos playback failed."
        return result

    result["success"] = True
    result["message"] = "Sonos speaker test successful."
    return result


def format_sonos_speaker_summary(result: dict) -> str:
    lines = [
        "George 3 Sonos Speaker Test",
        "",
        f"Speaker: {result['sonos_name']} ({result['sonos_ip']})",
        f"Phrase: {result['phrase']}",
        f"Local IP: {result['local_ip'] or '(not resolved)'}",
        f"Audio URL: {result['audio_url'] or '(not served)'}",
        f"WAV: {'OK' if result['wav'].get('success') else 'ERROR'}",
    ]

    playback = result.get("playback") or {}
    if playback:
        lines.extend(
            [
                f"Playback: {'OK' if playback.get('success') else 'ERROR'}",
                f"Reported speaker: {playback.get('speaker_name', '(unknown)')}",
                f"Volume: {playback.get('volume', '(unknown)')}",
                f"Mute: {playback.get('mute', '(unknown)')}",
            ]
        )

        for poll in playback.get("polls", []):
            lines.append(
                f"t+{poll['second']}s: {poll['state']} "
                f"position={poll['position']} duration={poll['duration']}"
            )

    lines.extend(["", f"Result: {'SUCCESS' if result['success'] else 'ERROR'}"])

    if result["message"]:
        lines.append(f"Message: {result['message']}")

    if result["error"]:
        lines.append(f"Error: {result['error']}")

    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description="Run an isolated Sonos speaker output test.")
    parser.add_argument("phrase", nargs="?", default=DEFAULT_PHRASE)
    parser.add_argument("--sonos-ip", default=None)
    parser.add_argument("--sonos-name", default=None)
    parser.add_argument("--poll-seconds", type=int, default=6)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_sonos_speaker_test(
        phrase=args.phrase,
        sonos_ip=args.sonos_ip,
        sonos_name=args.sonos_name,
        poll_seconds=args.poll_seconds,
    )
    print(format_sonos_speaker_summary(result))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
