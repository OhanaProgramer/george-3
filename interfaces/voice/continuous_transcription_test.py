"""Isolated continuous capture and transcription test for George."""

from __future__ import annotations

import argparse
import array
import math
import os
import shutil
import subprocess
import sys
import termios
import tempfile
import threading
import tty
import wave
from pathlib import Path
from typing import Callable, Sequence

from config import settings
from interfaces.voice.mic_capture_test import capture_audio_for_test
from shared.audio_devices.voice_devices import discover_voice_devices


DEFAULT_CHUNK_SECONDS = 3
DEFAULT_TMP_DIR = Path("/tmp/george_continuous_transcription")
DEFAULT_MODEL_FILE = Path("shared/models/whisper/ggml-base.en.bin")
DEFAULT_WHISPER_COMMAND = "whisper-cli"
DEFAULT_INPUT_HINT = "reSpeaker"
DEFAULT_MIN_RMS_DBFS = -55.0
LOCAL_TOOL_PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"


def run_command(command, timeout_seconds=120):
    env = os.environ.copy()
    env["PATH"] = LOCAL_TOOL_PATH
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=timeout_seconds,
        env=env,
    )


def resolve_project_path(path: Path | str) -> Path:
    resolved = Path(path)

    if resolved.is_absolute():
        return resolved

    return Path(__file__).resolve().parents[2] / resolved


def parse_whisper_cpp_output(stdout: str) -> str:
    transcript_lines = []

    for raw_line in stdout.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("[") and "]" in line:
            line = line.split("]", 1)[1].strip()

        if line:
            transcript_lines.append(line)

    return " ".join(transcript_lines).strip()


def transcribe_audio_for_test(
    input_file: Path,
    model_file: Path | str = DEFAULT_MODEL_FILE,
    whisper_command: str = DEFAULT_WHISPER_COMMAND,
    command_runner: Callable = run_command,
) -> dict:
    model_path = resolve_project_path(model_file)
    input_path = Path(input_file)

    result = {
        "success": False,
        "engine": "whisper.cpp",
        "command": whisper_command,
        "model_file": str(model_path),
        "input_file": str(input_path),
        "transcript": "",
        "message": "",
        "error": "",
    }

    if not model_path.exists():
        result["error"] = "whisper.cpp model file was not found."
        return result

    if not input_path.exists():
        result["error"] = "Input audio file was not found."
        return result

    command = [
        whisper_command,
        "-m",
        str(model_path),
        "-f",
        str(input_path),
        "-l",
        "en",
        "-nt",
        "-np",
    ]

    try:
        command_result = command_runner(command, timeout_seconds=120)
    except subprocess.TimeoutExpired as exc:
        result["error"] = f"whisper.cpp timed out after {exc.timeout} seconds."
        return result
    except OSError as exc:
        result["error"] = str(exc)
        return result

    if command_result.returncode != 0:
        result["error"] = command_result.stderr.strip() or "whisper.cpp failed."
        return result

    transcript = parse_whisper_cpp_output(command_result.stdout)
    result["success"] = True
    result["transcript"] = transcript
    result["message"] = "Audio transcribed."
    return result


def measure_wav_level(input_file: Path) -> dict:
    result = {
        "success": False,
        "rms_dbfs": -120.0,
        "max_dbfs": -120.0,
        "error": "",
    }

    try:
        with wave.open(str(input_file), "rb") as wav_file:
            sample_width = wav_file.getsampwidth()
            frames = wav_file.readframes(wav_file.getnframes())
    except (OSError, EOFError, wave.Error) as exc:
        result["error"] = str(exc)
        return result

    if not frames:
        result["success"] = True
        return result

    if sample_width != 2:
        result["error"] = f"Unsupported sample width for level check: {sample_width}"
        return result

    samples = array.array("h")
    samples.frombytes(frames)

    if sys.byteorder != "little":
        samples.byteswap()

    if not samples:
        result["success"] = True
        return result

    peak = float(2 ** 15)
    sum_squares = sum(sample * sample for sample in samples)
    rms = math.sqrt(sum_squares / len(samples))
    max_amp = max(abs(sample) for sample in samples)

    result["success"] = True
    result["rms_dbfs"] = -120.0 if rms <= 0 else round(20 * math.log10(rms / peak), 2)
    result["max_dbfs"] = -120.0 if max_amp <= 0 else round(20 * math.log10(max_amp / peak), 2)
    return result


def has_enough_audio(level: dict, min_rms_dbfs: float = DEFAULT_MIN_RMS_DBFS) -> bool:
    return bool(level.get("success")) and level.get("rms_dbfs", -120.0) >= min_rms_dbfs


def ensure_input_hint(default_hint: str = DEFAULT_INPUT_HINT) -> str:
    if not settings.VOICE_INPUT_DEVICE_HINT:
        settings.VOICE_INPUT_DEVICE_HINT = os.getenv("START_TALKING_INPUT_HINT", default_hint)

    return settings.VOICE_INPUT_DEVICE_HINT


def format_microphones(microphones: list[dict]) -> list[str]:
    if not microphones:
        return ["- none found"]

    return [f"- {device.get('name', 'unknown')}" for device in microphones]


def wait_for_key(stop_event: threading.Event, input_stream=None, output_writer: Callable[[str], None] = print):
    input_stream = input_stream or sys.stdin
    output_writer("Press any key to stop.")

    if not input_stream.isatty():
        input("Press ENTER to stop.")
        stop_event.set()
        return

    fd = input_stream.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)
        input_stream.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    stop_event.set()


def run_continuous_transcription_test(
    chunk_seconds: int = DEFAULT_CHUNK_SECONDS,
    tmp_dir: Path = DEFAULT_TMP_DIR,
    stop_event: threading.Event | None = None,
    capture_runner: Callable = capture_audio_for_test,
    transcription_runner: Callable = transcribe_audio_for_test,
    discovery_reader: Callable = discover_voice_devices,
    output_writer: Callable[[str], None] = print,
    cleanup: bool = True,
    max_chunks: int | None = None,
    show_files: bool = False,
    min_rms_dbfs: float = DEFAULT_MIN_RMS_DBFS,
    level_reader: Callable = measure_wav_level,
) -> dict:
    input_hint = ensure_input_hint()
    stop_event = stop_event or threading.Event()
    tmp_dir.mkdir(parents=True, exist_ok=True)
    discovery = discovery_reader()

    result = {
        "success": False,
        "chunk_seconds": chunk_seconds,
        "chunks": 0,
        "run_dir": "",
        "transcripts": [],
        "errors": [],
        "skipped_silence": 0,
        "message": "",
    }

    output_writer("George 3 Continuous Transcription Test")
    output_writer("")
    output_writer(f"Chunk duration: {chunk_seconds} seconds")
    output_writer(f"Input hint: {input_hint}")
    output_writer(f"Microphone count: {len(discovery.get('microphones', []))}")
    output_writer("Input devices:")
    for line in format_microphones(discovery.get("microphones", [])):
        output_writer(line)
    output_writer("")
    output_writer("Start talking...")
    output_writer("")

    run_dir = Path(tempfile.mkdtemp(prefix="run_", dir=tmp_dir))
    result["run_dir"] = str(run_dir)
    chunk_index = 0

    try:
        while not stop_event.is_set():
            if max_chunks is not None and chunk_index >= max_chunks:
                break

            chunk_index += 1
            audio_file = run_dir / f"chunk_{chunk_index:04d}.wav"
            if audio_file.exists():
                audio_file.unlink()
            output_writer("Listening...")

            capture = capture_runner(seconds=chunk_seconds, output_file=audio_file)
            result["chunks"] = chunk_index

            if not capture.get("success"):
                error = capture.get("error") or "Capture failed."
                result["errors"].append(error)
                output_writer(f"Capture error: {error}")
                continue

            if show_files:
                size_bytes = audio_file.stat().st_size if audio_file.exists() else 0
                output_writer(f"Audio file: {audio_file} ({size_bytes} bytes)")

            level = level_reader(audio_file)
            if show_files and level.get("success"):
                output_writer(
                    f"Audio level: rms={level['rms_dbfs']} dBFS max={level['max_dbfs']} dBFS"
                )

            if not has_enough_audio(level, min_rms_dbfs=min_rms_dbfs):
                result["skipped_silence"] += 1
                if show_files:
                    output_writer("Silence detected; skipping transcription.")
                output_writer("")
                continue

            transcription = transcription_runner(audio_file)

            if not transcription.get("success"):
                error = transcription.get("error") or "Transcription failed."
                result["errors"].append(error)
                output_writer(f"Transcription error: {error}")
                continue

            transcript = transcription.get("transcript", "").strip()

            if transcript:
                result["transcripts"].append(transcript)
                output_writer(f"Transcript: {transcript}")
                if show_files:
                    output_writer(f"Transcript source: {transcription.get('input_file', audio_file)}")

            output_writer("")
    except KeyboardInterrupt:
        output_writer("")
        output_writer("Stopping continuous transcription.")
    finally:
        if cleanup:
            shutil.rmtree(run_dir, ignore_errors=True)

    result["success"] = True
    result["message"] = "Continuous transcription stopped cleanly."
    return result


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description="Run isolated continuous capture and transcription.")
    parser.add_argument("--chunk-seconds", type=int, default=DEFAULT_CHUNK_SECONDS)
    parser.add_argument("--tmp-dir", default=str(DEFAULT_TMP_DIR))
    parser.add_argument("--keep-files", action="store_true")
    parser.add_argument("--show-files", action="store_true")
    parser.add_argument("--min-rms-dbfs", type=float, default=DEFAULT_MIN_RMS_DBFS)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    stop_event = threading.Event()
    key_thread = threading.Thread(target=wait_for_key, args=(stop_event,), daemon=True)
    key_thread.start()

    result = run_continuous_transcription_test(
        chunk_seconds=args.chunk_seconds,
        tmp_dir=Path(args.tmp_dir),
        stop_event=stop_event,
        cleanup=not args.keep_files,
        show_files=args.show_files,
        min_rms_dbfs=args.min_rms_dbfs,
    )

    print(result["message"])
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
