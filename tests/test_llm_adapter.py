"""LLM adapter tests.

Purpose: Verify configured LLM provider behavior without live API calls.
Phase: LLM Adapter v1.
Last updated: 2026-05-31.
Notes: Uses fake clients; does not call OpenAI.
"""

import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

from shared.llm import llm_adapter


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, model, input):
        self.calls.append({"model": model, "input": input})
        return SimpleNamespace(output_text="Hello from George.")


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


class LLMAdapterTests(unittest.TestCase):
    @contextmanager
    def llm_settings(
        self,
        provider="openai",
        fast_model="gpt-5.4-mini",
        deep_model="gpt-5.5",
        default_tier="fast",
        api_key="test-key",
    ):
        with (
            patch.object(llm_adapter.settings, "LLM_PROVIDER", provider),
            patch.object(llm_adapter.settings, "LLM_FAST_MODEL", fast_model),
            patch.object(llm_adapter.settings, "LLM_DEEP_MODEL", deep_model),
            patch.object(llm_adapter.settings, "LLM_DEFAULT_TIER", default_tier),
            patch.object(llm_adapter.settings, "OPENAI_API_KEY", api_key),
        ):
            yield

    def test_successful_mocked_response(self):
        fake_client = FakeClient()

        with self.llm_settings():
            result = llm_adapter.ask_llm(
                "Hello George",
                client_factory=lambda api_key: fake_client,
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["model"], "gpt-5.4-mini")
        self.assertEqual(result["tier"], "fast")
        self.assertEqual(result["input_text"], "Hello George")
        self.assertEqual(result["response_text"], "Hello from George.")
        self.assertEqual(result["message"], "LLM response received.")
        self.assertEqual(result["error"], "")
        self.assertEqual(fake_client.responses.calls, [{"model": "gpt-5.4-mini", "input": "Hello George"}])

    def test_missing_api_key(self):
        with self.llm_settings(api_key=""):
            result = llm_adapter.ask_llm("Hello George", client_factory=lambda api_key: FakeClient())

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "OPENAI_API_KEY is not configured.")

    def test_unsupported_provider(self):
        with self.llm_settings(provider="other"):
            result = llm_adapter.ask_llm("Hello George", client_factory=lambda api_key: FakeClient())

        self.assertFalse(result["success"])
        self.assertEqual(result["provider"], "other")
        self.assertEqual(result["error"], "Unsupported LLM provider: other")

    def test_blank_input(self):
        with self.llm_settings():
            result = llm_adapter.ask_llm("   ", client_factory=lambda api_key: FakeClient())

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "No input text provided.")

    def test_fast_tier_model_selection(self):
        fake_client = FakeClient()

        with self.llm_settings():
            result = llm_adapter.ask_llm(
                "Fast please",
                tier="fast",
                client_factory=lambda api_key: fake_client,
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "gpt-5.4-mini")
        self.assertEqual(fake_client.responses.calls[0]["model"], "gpt-5.4-mini")

    def test_deep_tier_model_selection(self):
        fake_client = FakeClient()

        with self.llm_settings():
            result = llm_adapter.ask_llm(
                "Think deeply",
                tier="deep",
                client_factory=lambda api_key: fake_client,
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "gpt-5.5")
        self.assertEqual(fake_client.responses.calls[0]["model"], "gpt-5.5")


if __name__ == "__main__":
    unittest.main()
