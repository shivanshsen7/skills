---
name: nano-banana-pro-google-ai-studio
description: 'Generate or edit images directly via Google AI Studio (Gemini Developer API) with the Gemini 3 Pro Image model — no OpenRouter markup. Use for prompt-only image generation, image edits, and multi-image compositing; supports 1K/2K/4K output.'
metadata:
  emoji: 🍌
  requires:
    bins:
      - uv
    env:
      - GEMINI_API_KEY
  primaryEnv: GEMINI_API_KEY
---

# Nano Banana Pro — Google AI Studio (direct)

## Overview

Generate or edit images by calling the Gemini Developer API directly with the
`google-genai` SDK — the same `gemini-3-pro-image-preview` model as
`nano-banana-pro-openrouter`, but hit straight against Google AI Studio instead
of routed through OpenRouter. Use this one whenever the user already holds a
Google AI Studio key: it skips OpenRouter's per-call markup entirely. Reach
for the OpenRouter sibling skill only when there's a specific reason to route
through OpenRouter instead (e.g. its zero-data-retention or provider-pinning
controls, or no direct key is available).

### Prompt-only generation

```
uv run {baseDir}/scripts/generate_image.py \
  --prompt "A cinematic sunset over snow-capped mountains" \
  --filename sunset.png
```

### Edit a single image

```
uv run {baseDir}/scripts/generate_image.py \
  --prompt "Replace the sky with a dramatic aurora" \
  --input-image input.jpg \
  --filename aurora.png
```

### Compose multiple images

```
uv run {baseDir}/scripts/generate_image.py \
  --prompt "Combine the subjects into a single studio portrait" \
  --input-image face1.jpg \
  --input-image face2.jpg \
  --filename composite.png
```

## Resolution

- Use `--resolution` with `1K`, `2K`, or `4K`.
- Default is `1K` if not specified.

## System prompt customization

The skill reads an optional system prompt from `assets/SYSTEM_TEMPLATE`. This
allows you to customize the image generation behavior without modifying code.

## Behavior and constraints

- Accept up to 3 input images via repeated `--input-image`.
- `--filename` accepts relative paths (saves to current directory) or absolute paths.
- If multiple images are returned, append `-1`, `-2`, etc. to the filename.
- Print `MEDIA: <path>` for each saved image. Do not read images back into the response.
- Don't run this automatically just because a post needs an image — generating
  costs the user's own API quota. Only run it when explicitly asked to
  generate (as opposed to just drafting/recommending a prompt).

## A note on the API surface

This script was written against the documented `google-genai` SDK patterns
(client, `generate_content`, `response_modalities`, inline-data image parts).
The exact config field for resolution (`image_config`) and the model id
(`gemini-3-pro-image-preview`) could not be verified against live Google docs
from this environment — no network access to `ai.google.dev` here. First run:
if the call fails with an unrecognized-field or model-not-found error, check
the current Gemini API docs for the right field/model name and fix the two
spots marked `MODEL` and `image_config` in `scripts/generate_image.py`.

## Troubleshooting

If the script exits non-zero, check stderr against these common blockers:

| Symptom | Resolution |
|---------|------------|
| `GEMINI_API_KEY is not set` | Ask the user to set it. bash: `export GEMINI_API_KEY="..."` |
| `uv: command not found` or not recognized | macOS/Linux: <code>curl -LsSf https://astral.sh/uv/install.sh &#124; sh</code>. Windows: <code>powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 &#124; iex"</code>. Then restart the terminal. |
| `PermissionDenied` / 403 / auth error | Key is invalid, or the AI Studio project doesn't have image-gen access yet. Verify at <https://aistudio.google.com/app/apikey>. |
| Model not found / unrecognized field in config | The model id or `image_config` schema in the script is stale — see "A note on the API surface" above. |

For transient errors (HTTP 429, network timeouts), retry once after 30
seconds. Do not retry the same error more than twice — surface the issue to
the user instead.
