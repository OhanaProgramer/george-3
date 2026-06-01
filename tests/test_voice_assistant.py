"""Voice assistant tests.

Purpose: Verify hear-think-speak orchestration.
Phase: Voice Assistant v1.
Last updated: 2026-05-31.
Notes: Uses fake runners; does not require a microphone, Whisper, OpenAI, or audio output.
"""

import unittest

from modules.voice_assistant import voice_assistant


def push_to_talk_result(success=True, transcript="What is the capital of France?", error=""):
    return {
        "success": success,
        "capture": {"success": success},
        "transcription": {"success": success},
        "transcript": transcript if success else "",
        "message": "Push-to-talk captured and transcribed audio." if success else "",
        "error": error,
    }


def llm_result(success=True, response_text="The capital of France is Paris.", error=""):
    return {
        "success": success,
        "provider": "openai",
        "model": "gpt-5.4-mini",
        "tier": "fast",
        "input_text": "What is the capital of France?",
        "response_text": response_text if success else "",
        "message": "LLM response received." if success else "",
        "error": error,
    }


def speech_result(success=True, error=""):
    return {
        "success": success,
        "engine": "apple",
        "voice": "Daniel",
        "message": "Spoke text." if success else "",
        "error": error,
    }


class VoiceAssistantTests(unittest.TestCase):
    def test_structured_result_shape(self):
        result = voice_assistant.run_voice_assistant(
            push_to_talk_runner=lambda: push_to_talk_result(),
            llm_runner=lambda transcript: llm_result(),
            speak_runner=lambda response: speech_result(),
        )

        self.assertEqual(
            set(result.keys()),
            {
                "success",
                "transcript",
                "llm_response",
                "capture",
                "transcription",
                "llm",
                "speech",
                "message",
                "error",
            },
        )

    def test_success_path(self):
        seen = {}

        def fake_llm(transcript):
            seen["transcript"] = transcript
            return llm_result(response_text="The capital of France is Paris.")

        def fake_speak(response):
            seen["response"] = response
            return speech_result()

        result = voice_assistant.run_voice_assistant(
            push_to_talk_runner=lambda: push_to_talk_result(),
            llm_runner=fake_llm,
            speak_runner=fake_speak,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["transcript"], "What is the capital of France?")
        self.assertEqual(result["llm_response"], "The capital of France is Paris.")
        self.assertEqual(result["message"], "Voice assistant completed.")
        self.assertEqual(result["error"], "")
        self.assertEqual(seen["transcript"], "What is the capital of France?")
        self.assertEqual(seen["response"], "The capital of France is Paris.")

    def test_transcription_failure_stops_immediately(self):
        def fail_if_called(value):
            raise AssertionError("downstream runner should not be called")

        result = voice_assistant.run_voice_assistant(
            push_to_talk_runner=lambda: push_to_talk_result(success=False, error="Transcription failed"),
            llm_runner=fail_if_called,
            speak_runner=fail_if_called,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["llm"], {})
        self.assertEqual(result["speech"], {})
        self.assertEqual(result["error"], "Transcription failed")

    def test_llm_failure_does_not_speak(self):
        def fail_if_called(value):
            raise AssertionError("speak should not be called")

        result = voice_assistant.run_voice_assistant(
            push_to_talk_runner=lambda: push_to_talk_result(),
            llm_runner=lambda transcript: llm_result(success=False, error="LLM failed"),
            speak_runner=fail_if_called,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["speech"], {})
        self.assertEqual(result["error"], "LLM failed")

    def test_speech_failure_returns_response_and_error(self):
        result = voice_assistant.run_voice_assistant(
            push_to_talk_runner=lambda: push_to_talk_result(),
            llm_runner=lambda transcript: llm_result(response_text="The capital of France is Paris."),
            speak_runner=lambda response: speech_result(success=False, error="say failed"),
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["llm_response"], "The capital of France is Paris.")
        self.assertEqual(result["speech"]["error"], "say failed")
        self.assertEqual(result["error"], "say failed")


if __name__ == "__main__":
    unittest.main()
