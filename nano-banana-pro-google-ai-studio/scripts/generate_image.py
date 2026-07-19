#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
# ]
# ///
"""
Generate or edit images directly via Google AI Studio (Gemini Developer API)
using the google-genai SDK. No OpenRouter involved.
"""

import argparse
import mimetypes
import os
from pathlib import Path

from google import genai
from google.genai import types


# Configuration
MAX_INPUT_IMAGES = 3
MODEL = "gemini-3-pro-image-preview"
MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate or edit images via Google AI Studio (direct)."
    )
    parser.add_argument("--prompt", required=True, help="Prompt describing the desired image.")
    parser.add_argument("--filename", required=True, help="Output filename (relative to CWD).")
    parser.add_argument(
        "--resolution",
        type=str.upper,
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 1K, 2K, or 4K.",
    )
    parser.add_argument(
        "--input-image",
        action="append",
        default=[],
        help=f"Optional input image path (repeatable, max {MAX_INPUT_IMAGES}).",
    )
    return parser.parse_args()


def require_api_key():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set in the environment.")
    return api_key


def load_system_prompt():
    """Load system prompt from assets/SYSTEM_TEMPLATE if it exists and is not empty."""
    script_dir = Path(__file__).parent.parent
    template_path = script_dir / "assets" / "SYSTEM_TEMPLATE"

    if template_path.exists():
        content = template_path.read_text(encoding="utf-8").strip()
        if content:
            return content
    return None


def build_contents(prompt: str, input_images: list[str]) -> list:
    parts = [types.Part.from_text(text=prompt)]
    for image_path in input_images:
        path = Path(image_path)
        if not path.exists():
            raise SystemExit(f"Input image not found: {path}")
        mime, _ = mimetypes.guess_type(str(path))
        if not mime:
            mime = "image/png"
        parts.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime))
    return [types.Content(role="user", parts=parts)]


def resolve_output_path(filename: str, image_index: int, total_count: int, mime: str) -> Path:
    output_path = Path(filename)
    suffix = output_path.suffix

    # Validate/correct suffix matches MIME type
    expected_suffix = MIME_TO_EXT.get(mime, ".png")
    if suffix and suffix.lower() != expected_suffix.lower():
        print(
            f"Warning: filename extension '{suffix}' doesn't match returned "
            f"MIME type '{mime}'. Using '{expected_suffix}' instead."
        )
        suffix = expected_suffix
    elif not suffix:
        suffix = expected_suffix

    # Single image: use original stem + corrected suffix
    if total_count <= 1:
        return output_path.with_suffix(suffix)

    # Multiple images: append numbering
    return output_path.with_name(f"{output_path.stem}-{image_index + 1}{suffix}")


def main():
    args = parse_args()

    if len(args.input_image) > MAX_INPUT_IMAGES:
        raise SystemExit(f"Too many input images: {len(args.input_image)} (max {MAX_INPUT_IMAGES}).")

    client = genai.Client(api_key=require_api_key())

    config_kwargs = {
        "response_modalities": ["IMAGE", "TEXT"],
        # NOTE: field name/shape for resolution unverified against live docs —
        # see "A note on the API surface" in SKILL.md if this errors.
        "image_config": types.ImageConfig(image_size=args.resolution),
    }

    system_prompt = load_system_prompt()
    if system_prompt:
        config_kwargs["system_instruction"] = system_prompt

    response = client.models.generate_content(
        model=MODEL,
        contents=build_contents(args.prompt, args.input_image),
        config=types.GenerateContentConfig(**config_kwargs),
    )

    candidate = response.candidates[0] if response.candidates else None
    if not candidate or not candidate.content or not candidate.content.parts:
        raise SystemExit("No content returned by the API.")

    images = [part for part in candidate.content.parts if getattr(part, "inline_data", None)]
    if not images:
        raise SystemExit("No images returned by the API.")

    # Create output directory once before processing images
    output_base_path = Path(args.filename)
    if output_base_path.parent and str(output_base_path.parent) != ".":
        output_base_path.parent.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for idx, part in enumerate(images):
        mime = part.inline_data.mime_type or "image/png"
        raw = part.inline_data.data
        output_path = resolve_output_path(args.filename, idx, len(images), mime)
        output_path.write_bytes(raw)
        saved_paths.append(output_path.resolve())

    for path in saved_paths:
        print(f"Saved image to: {path}")
        print(f"MEDIA: {path}")


if __name__ == "__main__":
    main()
