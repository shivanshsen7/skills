---
name: gh-profile-builder
description: Build or upgrade a GitHub profile — the special <username>/<username> README repo, GitHub's native social-accounts field, and (optionally) a curated public showcase repo. Use when the user says their GitHub profile "looks bare", wants to "enrich"/"overhaul" their GitHub profile, asks to set up a profile README, or wants to pin/showcase real work publicly. Not a blind Q&A form — grounds the design in the person's actual site/work/brand before asking anything, and adapts to whatever image-generation or writing-voice skills happen to be installed rather than assuming a specific toolset.
argument-hint: "[github username] [--with-showcase-repo]"
---

# GitHub Profile Builder

Builds a GitHub profile that looks like it belongs to a specific person, not a template.
Two failure modes to avoid: a generic interview-driven profile that could belong to
anyone, and a showcase repo that quietly republishes someone else's work as the user's own.

## Process

0. **Ground the design in reality before asking anything.** Read the person's own site
   (design tokens, portfolio data, bio). Pull `gh api user`, `user/social_accounts`, and
   `users/<username>/repos` — don't ask for what's already derivable. Reserve direct
   questions for genuine taste calls.
1. **Discover installed capabilities — don't hardcode a toolset.** `ls .claude/skills/`
   at both project and user level; use whatever image-gen/rephrase/tracing skills exist
   rather than assuming a specific one, or say plainly if nothing's installed.
2. **Vet anything before presenting it as "their own work."** See
   `references/vetting.md` — the step most likely to be skipped under time pressure,
   and the costliest one to skip.
3. **Know GitHub's actual rendering constraints** before designing anything. See
   `references/github-rendering.md` — table-border and `<video>`-stripping gotchas,
   repo naming, column width, badges, pinning.
4. **Generating a banner/logo/favicon?** See `references/asset-generation.md`.
5. **Animating a mark or avatar?** See `references/video-generation.md` — framing
   drift, loop technique, and file size are distinct failure modes from static generation.
6. **Assemble**: banner → headline badges → 1-2 sentence bio → what they're actually
   doing now → Stack badge row → footer links. Adapt the shape to what step 0 surfaced.
7. **Ship**: show the assembled README before pushing, then push to
   `<username>/<username>` (pinning repos is a manual GitHub UI step, no reliable API).
   Run the full `references/qa-checklist.md` before and after.

## Reference material

Profile gallery: https://zzetao.github.io/awesome-github-profile/ · width research:
https://wh0.github.io/2025/05/18/banner-width.html — starting points, not a substitute
for a fresh look.
