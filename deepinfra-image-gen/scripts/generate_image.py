#!/usr/bin/env python3
"""
Generate images via DeepInfra's OpenAI-compatible image-generation endpoint.

Stdlib only (urllib.request, json, base64, argparse) — no pip/uv install needed.
Run with plain: python3 generate_image.py --prompt "..." --filename out.png

Endpoint verified against https://docs.deepinfra.com/apis/image-generation and
the model-specific /api pages for black-forest-labs/FLUX-1.1-pro and
black-forest-labs/FLUX-2-klein-9b (both use the same OpenAI-compatible route).
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.deepinfra.com/v1/openai/images/generations"
DEFAULT_MODEL = "black-forest-labs/FLUX-1.1-pro"
ENV_FILE = os.path.expanduser("~/.config/deepinfra/env")
REQUEST_TIMEOUT_SECS = 180


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate images via DeepInfra's text-to-image API."
    )
    parser.add_argument("--prompt", required=True, help="Text description of the desired image.")
    parser.add_argument(
        "--filename", required=True, help="Output filename (relative to CWD or absolute)."
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"DeepInfra model slug (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--width", type=int, default=1024, help="Image width in pixels (default: 1024)."
    )
    parser.add_argument(
        "--height", type=int, default=1024, help="Image height in pixels (default: 1024)."
    )
    parser.add_argument(
        "--size",
        default=None,
        help='Explicit "WIDTHxHEIGHT" string; overrides --width/--height if given.',
    )
    parser.add_argument(
        "--num-images",
        type=int,
        default=1,
        help="Number of images to generate, 1-4 (default: 1).",
    )
    return parser.parse_args()


def resolve_api_key():
    """
    Resolution order:
      1. DEEPINFRA_API_KEY environment variable.
      2. macOS Keychain (preferred storage): `security find-generic-password`.
      3. ~/.config/deepinfra/env (KEY=VALUE file, chmod 600 recommended).
    Never print or log the resolved key.
    """
    env_key = os.environ.get("DEEPINFRA_API_KEY")
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
            ["security", "find-generic-password", "-s", "DEEPINFRA_API_KEY", "-w"],
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
        if key == "DEEPINFRA_API_KEY" and value:
            return value
    return None


def key_not_found_message():
    return (
        "No DeepInfra API key found (checked DEEPINFRA_API_KEY env var, macOS Keychain, "
        f"and {ENV_FILE}).\n\n"
        "Store your key using one of these:\n\n"
        "  Preferred (macOS Keychain — interactive prompt, key never touches shell history):\n"
        '    security add-generic-password -s DEEPINFRA_API_KEY -a "$USER" -w\n\n'
        "  Alternative (env file):\n"
        f"    mkdir -p {os.path.dirname(ENV_FILE)}\n"
        f"    echo 'DEEPINFRA_API_KEY=your-key-here' > {ENV_FILE}\n"
        f"    chmod 600 {ENV_FILE}\n\n"
        "  Or export it for this shell session only:\n"
        "    export DEEPINFRA_API_KEY=your-key-here"
    )


def build_request_body(args):
    if args.size:
        size = args.size
    else:
        size = f"{args.width}x{args.height}"
    return {
        "model": args.model,
        "prompt": args.prompt,
        "size": size,
        "n": args.num_images,
        "response_format": "b64_json",
    }


def resolve_output_path(filename, index, total):
    output_path = Path(filename)
    suffix = output_path.suffix or ".png"
    if total <= 1:
        return output_path.with_suffix(suffix)
    return output_path.with_name(f"{output_path.stem}-{index + 1}{suffix}")


def main():
    args = parse_args()

    if not (1 <= args.num_images <= 4):
        print(
            f"Warning: --num-images {args.num_images} is outside DeepInfra's documented "
            "1-4 range; sending as-is.",
            file=sys.stderr,
        )

    api_key = resolve_api_key()
    if not api_key:
        print(key_not_found_message(), file=sys.stderr)
        sys.exit(1)

    body = build_request_body(args)
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
                "DeepInfra rejected the API key (HTTP 401 Unauthorized). "
                "The key is invalid, revoked, or malformed. Re-check the value stored via "
                "`security find-generic-password -s DEEPINFRA_API_KEY -w` (or the env file) "
                f"against your DeepInfra dashboard key.\nResponse body: {error_body}",
                file=sys.stderr,
            )
        elif e.code == 429:
            print(
                "DeepInfra rate-limited this request (HTTP 429). Wait and retry, or check "
                f"account usage/quota.\nResponse body: {error_body}",
                file=sys.stderr,
            )
        elif e.code == 404:
            print(
                f"Model '{args.model}' not found (HTTP 404). Verify the exact model slug "
                "against https://deepinfra.com/models/text-to-image.\n"
                f"Response body: {error_body}",
                file=sys.stderr,
            )
        else:
            print(
                f"DeepInfra API request failed: HTTP {e.code} {e.reason}\n"
                f"Response body: {error_body}",
                file=sys.stderr,
            )
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error reaching DeepInfra: {e.reason}", file=sys.stderr)
        sys.exit(1)

    data = payload.get("data")
    if not data:
        print(f"No image data returned by DeepInfra. Full response: {payload}", file=sys.stderr)
        sys.exit(1)

    output_base = Path(args.filename)
    if output_base.parent and str(output_base.parent) != ".":
        output_base.parent.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for idx, item in enumerate(data):
        b64_json = item.get("b64_json")
        if not b64_json:
            print(f"Item {idx} had no b64_json field: {item}", file=sys.stderr)
            continue
        raw = base64.b64decode(b64_json)
        output_path = resolve_output_path(args.filename, idx, len(data))
        output_path.write_bytes(raw)
        saved_paths.append(output_path.resolve())

    if not saved_paths:
        print("No images were saved (all response items lacked image data).", file=sys.stderr)
        sys.exit(1)

    for path in saved_paths:
        print(f"MEDIA: {path}")


if __name__ == "__main__":
    main()
