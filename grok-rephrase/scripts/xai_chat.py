#!/usr/bin/env python3
"""
Call xAI's Grok models directly (OpenAI-compatible chat completions endpoint).

Stdlib only (urllib.request, json, argparse) — no pip/uv install needed.
Run with plain: python3 xai_chat.py --prompt "..." [--persona "..."] [--model grok-4.3]

Endpoint: https://api.x.ai/v1/chat/completions (OpenAI-compatible).
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = "grok-4.3"
ENV_FILE = os.path.expanduser("~/.config/xai/env")
REQUEST_TIMEOUT_SECS = 120

DEFAULT_PERSONA = (
    "Practitioner voice bridging academic AI research and enterprise AI "
    "(Salesforce/Agentforce, agent architectures) — writes like someone who did "
    "the work, not someone summarizing it. Cut filler, active voice, name the "
    "real actor (never \"nobody\" or \"the system\"), no stale AI-filler (delve, "
    "leverage, unlock, game-changing, revolutionize) or dead metaphors (deep "
    "dive, move the needle, low-hanging fruit). Ground every claim in something "
    "concrete — a number, a failure, a specific thing that happened. Rephrase "
    "the given text in this voice. Return only the rephrased text, no "
    "commentary, no preamble."
)


def parse_args():
    parser = argparse.ArgumentParser(description="Call Grok models via xAI's direct API.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", "-p", help="Draft text / prompt to send.")
    source.add_argument("--file", help="Read the draft/prompt from a file path.")
    source.add_argument("--stdin", action="store_true", help="Read the draft/prompt from stdin.")
    parser.add_argument(
        "--persona",
        "--system",
        dest="persona",
        default=DEFAULT_PERSONA,
        help="Override the default rephrase persona with a custom system prompt.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"xAI model slug (default: {DEFAULT_MODEL}).",
    )
    return parser.parse_args()


def resolve_api_key():
    """
    Resolution order:
      1. XAI_API_KEY environment variable.
      2. macOS Keychain (preferred storage): `security find-generic-password`.
      3. ~/.config/xai/env (KEY=VALUE file, chmod 600 recommended).
    Never print or log the resolved key.
    """
    env_key = os.environ.get("XAI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    keychain_key = _read_from_keychain()
    if keychain_key:
        return keychain_key

    file_key = _read_from_env_file()
    if file_key:
        return file_key

    return None


def _read_from_keychain():
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "XAI_API_KEY", "-w"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _read_from_env_file():
    if not os.path.isfile(ENV_FILE):
        return None
    try:
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError:
        return None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key == "XAI_API_KEY" and value:
            return value
    return None


def key_not_found_message():
    return (
        "No xAI API key found (checked XAI_API_KEY env var, macOS Keychain, "
        f"and {ENV_FILE}).\n\n"
        "Store your key using one of these:\n\n"
        "  Preferred (macOS Keychain — interactive prompt, key never touches shell history):\n"
        '    security add-generic-password -s XAI_API_KEY -a "$USER" -w\n\n'
        "  Alternative (env file):\n"
        f"    mkdir -p {os.path.dirname(ENV_FILE)}\n"
        f"    echo 'XAI_API_KEY=your-key-here' > {ENV_FILE}\n"
        f"    chmod 600 {ENV_FILE}\n\n"
        "  Or export it for this shell session only:\n"
        "    export XAI_API_KEY=your-key-here"
    )


def resolve_input_text(args):
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.stdin:
        return sys.stdin.read()
    return args.prompt


def build_request_body(args, input_text):
    return {
        "model": args.model,
        "messages": [
            {"role": "system", "content": args.persona},
            {"role": "user", "content": input_text},
        ],
    }


def main():
    args = parse_args()

    input_text = resolve_input_text(args)
    if not input_text or not input_text.strip():
        print("Error: input text is empty.", file=sys.stderr)
        sys.exit(1)

    api_key = resolve_api_key()
    if not api_key:
        print(key_not_found_message(), file=sys.stderr)
        sys.exit(1)

    body = build_request_body(args, input_text)
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        if e.code == 401:
            print(
                "xAI rejected the API key (HTTP 401 Unauthorized). The key is invalid, "
                "revoked, or malformed. Re-check the value stored via "
                "`security find-generic-password -s XAI_API_KEY -w` (or the env file) "
                f"against your xAI console key.\nResponse body: {error_body}",
                file=sys.stderr,
            )
        elif e.code == 429:
            print(
                f"xAI rate-limited this request (HTTP 429). Wait and retry, or check "
                f"account usage/quota.\nResponse body: {error_body}",
                file=sys.stderr,
            )
        elif e.code == 404:
            print(
                f"Model '{args.model}' not found (HTTP 404). Verify the exact model slug "
                f"against your xAI console.\nResponse body: {error_body}",
                file=sys.stderr,
            )
        else:
            print(
                f"xAI API request failed: HTTP {e.code} {e.reason}\n"
                f"Response body: {error_body}",
                file=sys.stderr,
            )
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error reaching xAI: {e.reason}", file=sys.stderr)
        sys.exit(1)

    choices = payload.get("choices")
    if not choices:
        print(f"No response returned by xAI. Full response: {payload}", file=sys.stderr)
        sys.exit(1)

    message = choices[0].get("message", {})
    content = message.get("content")
    if not content:
        print(f"Response had no content. Full response: {payload}", file=sys.stderr)
        sys.exit(1)

    print(content)


if __name__ == "__main__":
    main()
