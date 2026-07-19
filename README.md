# Skills

A curated set of reusable AI-agent skills. Built for real use in day-to-day work — content generation, drafting tools, and repo/profile automation — not as demos.

Each skill is a self-contained directory with a `SKILL.md` (frontmatter + instructions an agent reads to decide when and how to use it) and, where needed, supporting scripts. Written in the [Claude Code](https://claude.com/claude-code) skill format; drop a directory into `.claude/skills/` (project-level) or `~/.claude/skills/` (user-level) to install it there. A few of these also declare compatibility with other agent platforms (Cursor, Codex, Gemini CLI) in their frontmatter — check each skill's own metadata.

## Skills

| Skill | Description |
| --- | --- |
| [`grok-rephrase`](./grok-rephrase) | Get a second-opinion rephrase of a draft from xAI's Grok, called directly against the xAI API — no OpenRouter markup. Also usable as a generic direct-xAI prompt caller. |
| [`deepinfra-image-gen`](./deepinfra-image-gen) | Generate images via DeepInfra's API (FLUX and other text-to-image models). Prompt-only generation — not image editing or compositing. |
| [`nano-banana-pro-google-ai-studio`](./nano-banana-pro-google-ai-studio) | Generate or edit images directly via Google AI Studio (Gemini Developer API) with the Gemini 3 Pro Image model — no OpenRouter markup. Supports prompt-only generation, edits, and multi-image compositing at 1K/2K/4K. |
| [`nano-banana-pro-openrouter`](./nano-banana-pro-openrouter) | Same Gemini 3 Pro Image model and capabilities as above, routed through OpenRouter instead of a direct Google API key. |
| [`create-carousel`](./create-carousel) | Create LinkedIn carousel slides as HTML and export them to PDF using Playwright. |
| [`gh-profile-builder`](./gh-profile-builder) | Build or upgrade a GitHub profile: the special `<username>/<username>` README repo, GitHub's native social-accounts field, and optionally a curated public showcase repo. Grounds the design in the person's actual site/work rather than running a generic Q&A template. |

## Requirements

Each skill lists its own dependencies (binaries, environment variables for API keys) in its `SKILL.md` frontmatter under `metadata.requires`. Nothing here is bundled with credentials — bring your own API keys for the services each skill calls (xAI, DeepInfra, Google AI Studio, OpenRouter).

## License

No license file is included; treat this as source-available for reference. Open an issue if you want to reuse something and licensing terms aren't clear.
