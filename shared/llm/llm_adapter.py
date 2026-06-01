"""LLM adapter.

Purpose: Send text to the configured LLM provider and return text.
Phase: LLM Adapter v1.
Last updated: 2026-05-31.
Notes: Text in, text out only; no audio, routing, actions, or memory.
"""

from __future__ import annotations

import argparse

from config import settings


SUPPORTED_PROVIDER = "openai"
SUPPORTED_TIERS = {"fast", "deep"}


def create_openai_client(api_key):
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def ask_llm(input_text: str, tier=None, client_factory=create_openai_client) -> dict:
    selected_tier = tier or settings.LLM_DEFAULT_TIER
    model = select_model(selected_tier)
    result = {
        "success": False,
        "provider": settings.LLM_PROVIDER,
        "model": model,
        "tier": selected_tier,
        "input_text": input_text,
        "response_text": "",
        "message": "",
        "error": "",
    }

    if settings.LLM_PROVIDER != SUPPORTED_PROVIDER:
        result["error"] = f"Unsupported LLM provider: {settings.LLM_PROVIDER}"
        return result

    if selected_tier not in SUPPORTED_TIERS:
        result["error"] = f"Unsupported LLM tier: {selected_tier}"
        return result

    if not input_text or not input_text.strip():
        result["error"] = "No input text provided."
        return result

    if not settings.OPENAI_API_KEY:
        result["error"] = "OPENAI_API_KEY is not configured."
        return result

    try:
        client = client_factory(settings.OPENAI_API_KEY)
        response = client.responses.create(
            model=model,
            input=input_text,
        )
    except ImportError:
        result["error"] = "OpenAI SDK is not installed."
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result

    result["success"] = True
    result["response_text"] = getattr(response, "output_text", "").strip()
    result["message"] = "LLM response received."
    return result


def select_model(tier):
    if tier == "deep":
        return settings.LLM_DEEP_MODEL

    return settings.LLM_FAST_MODEL


def format_llm_summary(result):
    response_text = result["response_text"] if result["response_text"] else "(none)"
    lines = [
        "George 3 LLM Adapter",
        "",
        f"Provider: {result['provider']}",
        f"Tier: {result['tier']}",
        f"Model: {result['model']}",
        "",
        "Response:",
        response_text,
        "",
        f"Result: {'SUCCESS' if result['success'] else 'ERROR'}",
    ]

    if result["error"]:
        lines.extend(["", f"Error: {result['error']}"])

    return "\n".join(lines)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Send text to George's configured LLM provider.")
    parser.add_argument("input_text", nargs="*")
    parser.add_argument("--tier", choices=sorted(SUPPORTED_TIERS))
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    input_text = " ".join(args.input_text)
    print(format_llm_summary(ask_llm(input_text, tier=args.tier)))


if __name__ == "__main__":
    main()
