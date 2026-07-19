---
name: grok-rephrase
description: 'Rephrase a draft using xAI''s Grok models, called directly (no OpenRouter markup). Use when the user wants a Grok/xAI second opinion or alternate-voice rephrase of a paragraph, post, or file — e.g. "grok-rephrase this", "see what Grok does with this paragraph", "call Grok on this draft". Also usable as a generic direct-xAI caller (any prompt/model) when the rephrase framing doesn''t fit.'
argument-hint: "[file path or pasted draft]"
metadata:
  emoji: 🐦
  requires:
    bins:
      - python3
    env:
      - XAI_API_KEY
  primaryEnv: XAI_API_KEY
---

# Grok Rephrase

Call Grok directly via xAI's API to get an alternate rephrasing of a draft.
This is a **second-opinion / alternate-take tool**, not a replacement for
`shivansh-voice` — whatever Grok returns still needs to pass the
`shivansh-voice` cold-read pass before anything ships. Never paste Grok's
output straight into a shipping file.

## Usage

### Rephrase a draft (default persona)

```bash
python3 {baseDir}/scripts/xai_chat.py --file docs/drafts/my-post.md
```

### Rephrase pasted text

```bash
python3 {baseDir}/scripts/xai_chat.py --prompt "The system decided not to notify anyone."
```

### Override the persona (different voice than the default)

```bash
python3 {baseDir}/scripts/xai_chat.py --file draft.md \
  --persona "Rephrase this in your own unfiltered voice, no house-style constraints."
```

### Generic call (not a rephrase — any prompt, any system message)

```bash
python3 {baseDir}/scripts/xai_chat.py --prompt "Explain RLHF in two sentences." \
  --persona "You are a concise technical explainer." --model grok-4.3
```

## Default persona

When `--persona`/`--system` is omitted, the script uses a lean, hand-written
default distilled from `shivansh-voice`'s "Who's writing" description:
practitioner voice, active voice, name the real actor, no AI-filler or dead
metaphors, ground claims in something concrete, return only the rephrased
text.

This default is a **starting point, not a synced copy** — `shivansh-voice` is
a living document (its banned-phrase list is meant to grow); this skill's
default persona is intentionally kept short and does not track every future
edit to `shivansh-voice`. If the default persona starts feeling stale,
update the `DEFAULT_PERSONA` constant in `scripts/xai_chat.py` directly
rather than trying to keep it byte-for-byte in sync with `shivansh-voice`.

## Model choice

Default: **`grok-4.3`** — xAI's flagship general model, best instruction
following, right fit for prose rephrasing. Override with `--model` for other
Grok variants (e.g. a reasoning-focused or coding-focused model) — check the
xAI console for current model slugs and pricing before assuming a name is
still valid.

## API key resolution (in order)

1. `XAI_API_KEY` environment variable, if set.
2. **macOS Keychain (preferred storage)**:
   `security find-generic-password -s XAI_API_KEY -w`
3. `~/.config/xai/env` fallback file (`KEY=VALUE` lines, `#` comments
   ignored, optional `export ` prefix and quotes tolerated).

If no key is found anywhere, the script exits with the exact commands to
store one. To store a key the recommended way:

```bash
security add-generic-password -s XAI_API_KEY -a "$USER" -w
```
(interactive prompt — the key never lands in shell history)

Or the env-file alternative:
```bash
mkdir -p ~/.config/xai
echo 'XAI_API_KEY=your-key-here' > ~/.config/xai/env
chmod 600 ~/.config/xai/env
```

## Behavior and constraints

- Prints the model's response as plain text to stdout — never auto-writes
  or overwrites any file. Review the output before doing anything with it.
- No streaming — single blocking request/response.
- This calls xAI's paid API directly; only run it when the user actually
  wants a Grok rephrase, not automatically alongside every editorial pass.

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| "No xAI API key found" | Store a key via Keychain or the env file — see "API key resolution" above. |
| HTTP 401 Unauthorized | Key is invalid or revoked. Re-check the stored value against the xAI console key. |
| HTTP 429 | Rate-limited or over quota. Wait and retry, or check usage at the xAI console. |
| HTTP 404 / "Model not found" | Model slug is wrong or no longer available. Cross-check against the xAI console's model list. |
| Network error | Check connectivity to `api.x.ai`; if running in a sandboxed tool environment, this host may need an explicit allowlist entry. |

For transient errors (429, network timeouts), retry once after 30 seconds.
Do not retry the same error more than twice — surface the issue to the user
instead.
