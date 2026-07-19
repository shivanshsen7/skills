---
name: deepinfra-image-gen
description: 'Generate images via DeepInfra''s API (FLUX and other text-to-image models). Use when the user wants to generate an image via DeepInfra, FLUX, or wants cheaper/alternative image generation outside Google AI Studio / OpenRouter Nano Banana Pro. Not for image editing or compositing — prompt-only text-to-image generation only.'
metadata:
  emoji: 🌊
  requires:
    bins:
      - python3
    env:
      - DEEPINFRA_API_KEY
  primaryEnv: DEEPINFRA_API_KEY
---

# DeepInfra Image Generation

## Overview

Generate images by calling DeepInfra's OpenAI-compatible image-generation
endpoint directly over HTTP with Python's standard library — no SDK, no
`uv`/`pip` install. Reach for this skill when the user explicitly wants
DeepInfra or FLUX, or wants a cheaper alternative to Nano Banana Pro
(Gemini). It does not support image editing/compositing — prompt-only
text-to-image.

Verified against DeepInfra's live docs on 2026-07-13:
- Endpoint docs: https://docs.deepinfra.com/apis/image-generation
- Full parameter/response reference: https://docs.deepinfra.com/api-reference/image-generation/openai-images-generations.md
- Model page confirming the model slug and endpoint: https://deepinfra.com/black-forest-labs/FLUX-1.1-pro/api

## Usage

### Basic prompt-only generation

```
python3 {baseDir}/scripts/generate_image.py \
  --prompt "A cinematic sunset over snow-capped mountains" \
  --filename sunset.png
```

### Wide landscape (~1200x675, nearest FLUX-1.1-pro-supported size)

FLUX-1.1-pro's native range is 256-1440px per side, in multiples of 32.
1200x675 isn't a multiple of 32, so the nearest valid pair close to 16:9 is
1216x672:

```
python3 {baseDir}/scripts/generate_image.py \
  --prompt "A wide cinematic landscape shot of rolling hills at golden hour" \
  --filename landscape.png \
  --width 1216 --height 672
```

### Multiple images in one call

```
python3 {baseDir}/scripts/generate_image.py \
  --prompt "Studio product photo of a ceramic mug on white background" \
  --filename mug.png \
  --num-images 4
```
Saves as `mug-1.png`, `mug-2.png`, `mug-3.png`, `mug-4.png`.

### Using a different model

```
python3 {baseDir}/scripts/generate_image.py \
  --prompt "A minimalist line-art icon of a rocket" \
  --filename rocket.png \
  --model black-forest-labs/FLUX-2-klein-9b
```

## Model choice

- **Default: `black-forest-labs/FLUX-1.1-pro`** — Black Forest Labs' proprietary
  flagship model, described by DeepInfra as their "latest state-of-the-art"
  for prompt following, visual quality, detail, and output diversity.
  $0.04/image. This is the quality-first default.
- **`black-forest-labs/FLUX-2-klein-9b`** — cheaper/faster ($0.015/request,
  scaled by dimensions), DeepInfra's "best quality-to-latency ratio,
  production apps" model. Use when the user asks for cheap/fast generation
  over max quality.
- Full current list: https://deepinfra.com/models/text-to-image

## API key resolution (in order)

1. `DEEPINFRA_API_KEY` environment variable, if set.
2. **macOS Keychain (preferred storage)**:
   `security find-generic-password -s DEEPINFRA_API_KEY -w`
3. `~/.config/deepinfra/env` fallback file (`KEY=VALUE` lines, `#` comments
   ignored, optional `export ` prefix and quotes tolerated).

If no key is found anywhere, the script exits with the exact commands to
store one. To store a key the recommended way:

```bash
security add-generic-password -s DEEPINFRA_API_KEY -a "$USER" -w
```
(interactive prompt — the key never lands in shell history)

Or the env-file alternative:
```bash
mkdir -p ~/.config/deepinfra
echo 'DEEPINFRA_API_KEY=your-key-here' > ~/.config/deepinfra/env
chmod 600 ~/.config/deepinfra/env
```

## Resolution / size

- `--width`/`--height` (defaults 1024x1024) are combined into the API's
  `size` string (`"WIDTHxHEIGHT"`). `--size` overrides both if passed
  directly (e.g. `--size 1024x1792`).
- DeepInfra's docs state size "depend[s] on the model" without a fixed enum.
  For `FLUX-1.1-pro` specifically, the model's own demo page documents a
  256-1440px range per side, in multiples of 32 — stay within that range for
  this model.
- `--num-images` (default 1) maps to the API's `n` parameter; documented
  range is 1-4.

## Behavior and constraints

- Response format is fixed to `b64_json` (the only format DeepInfra's
  OpenAI-compatible endpoint supports); the script base64-decodes and writes
  each image straight to disk.
- Multiple images append `-1`, `-2`, etc. to `--filename`.
- Prints `MEDIA: <path>` for each saved image.
- Never run this automatically just because content needs an image —
  generation costs the user's own DeepInfra balance. Only run when explicitly
  asked to generate (not just to draft/recommend a prompt).

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| "No DeepInfra API key found" | Store a key via Keychain or the env file — see "API key resolution" above. |
| HTTP 401 Unauthorized | Key is invalid or revoked. Re-check the stored value against the DeepInfra dashboard key. |
| HTTP 429 | Rate-limited or over quota. Wait and retry, or check usage at the DeepInfra dashboard. |
| HTTP 404 / "Model not found" | Model slug is wrong or no longer hosted. Cross-check against https://deepinfra.com/models/text-to-image. |
| HTTP 422 | Validation error — usually an out-of-range `size` for the chosen model (e.g. not a multiple of 32, or outside 256-1440 for FLUX-1.1-pro). Check the response body the script prints. |

For transient errors (429, network timeouts), retry once after 30 seconds.
Do not retry the same error more than twice — surface the issue to the user
instead.

## A note on docs ambiguity

DeepInfra's OpenAI-compatible endpoint documentation states `size` "depend[s]
on the model" but doesn't publish a per-model enum in the API reference
itself. The concrete 256-1440/multiple-of-32 constraint used above for
FLUX-1.1-pro comes from that model's own demo-page parameter description, not
from the shared OpenAI-compatible reference page — treat it as
model-specific, not universal, if switching models.
