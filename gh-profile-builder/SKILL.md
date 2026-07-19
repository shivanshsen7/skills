---
name: gh-profile-builder
description: Build or upgrade a GitHub profile — the special <username>/<username> README repo, GitHub's native social-accounts field, and (optionally) a curated public showcase repo. Use when the user says their GitHub profile "looks bare", wants to "enrich"/"overhaul" their GitHub profile, asks to set up a profile README, or wants to pin/showcase real work publicly. Not a blind Q&A form — grounds the design in the person's actual site/work/brand before asking anything, and adapts to whatever image-generation or writing-voice skills happen to be installed rather than assuming a specific toolset.
argument-hint: "[github username] [--with-showcase-repo]"
---

# GitHub Profile Builder

Builds a GitHub profile that looks like it belongs to a specific person, not a template.
The two failure modes this skill exists to avoid: (1) a generic interview-driven profile
that could belong to anyone once you swap the name, and (2) a showcase repo that quietly
republishes someone else's work as the user's own.

## 0. Ground the design in reality before asking anything

Do not open with an interview. Interview questions produce generic answers; the person's
own site, repos, and existing bio produce specific ones. Before asking the user anything:

- If working inside one of the person's own repos, read whatever encodes their actual
  brand/voice: a design-tokens file (`DESIGN.md`, a Tailwind theme, a `settings.ts`/`site.config`
  singleton), real project/portfolio data, an existing bio or resume.
- Pull their current GitHub state: `gh api user` (bio, company, location, existing avatar),
  `gh api user/social_accounts` (already-registered links — don't ask for links that are
  already there), `gh api users/<username>/repos` (what's public today, what could be pinned).
- Only ask the user directly for what genuinely isn't derivable: which of several plausible
  directions they want, confirmation before anything goes live, taste calls (this shape vs.
  that one). Keep it to a handful of pointed questions, not a form.

## 1. Discover what capabilities actually exist — don't hardcode a toolset

This skill runs for people with completely different local setups. Never assume a specific
image-gen or rephrase skill is installed by name. Instead, at the start of a run:

- List `.claude/skills/` at both project and user level (`ls .claude/skills/ ~/.claude/skills/`)
  and skim names/descriptions for categories this workflow can use: image generation/editing,
  writing-voice/rephrase second-opinions, carousel/social-asset builders, vector tracing.
- If an image-generation skill exists, use it for the banner/logo — don't tell the user to go
  generate one manually elsewhere unless nothing is available.
- If a rephrase/voice-check skill exists, run the drafted bio/copy through it as a second
  opinion before shipping — but treat its output as a second opinion, not a pasteable final.
- If nothing relevant is installed, say so plainly and offer to draft prompts/copy for the
  user to run through whatever web tool they have, rather than silently skipping the step.


## 2. Vet anything before presenting it as "their own work"

This is the step most likely to be skipped under time pressure, and the one with the most
real cost if skipped — republishing someone else's content as the user's own is a
misattribution problem, not just a taste problem. Before including ANY file, skill, snippet,
or project in something public-facing:

- Check for third-party origin markers: an `origin:`, `author:`, `source:`, or `license:`
  field in frontmatter that names anyone other than the user; a `source: community` tag; body
  text like "curated by X" or "prompts from X". Any of these means: exclude it, or ask the
  user to confirm explicit permission/attribution before including it.
- Grep candidate content for secrets and leakage before it goes anywhere public: API keys,
  internal hostnames, other local file paths, employer names. (`grep -rniE
  "api[_-]?key\s*=\s*['\"]|sk-[a-zA-Z0-9]{20}|password\s*=\s*['\"]"` as a baseline pass — adapt
  to what the content actually is.)
- Check the user's own memory/notes for any documented employment or publishing-consent
  constraints (outside-work clauses, employer approval requirements) before publishing
  anything new publicly. If such a constraint exists, surface it and get explicit
  confirmation rather than silently proceeding — this is genuinely their call, not a default.
- When multiple candidate items exist (e.g. a folder of skills, projects, certifications to showcase), present the
  vetting result as a clear include/exclude list with the reason for each exclusion, and let
  the user confirm the final set rather than deciding unilaterally.

## 3. Know GitHub's actual rendering constraints

Save a wasted design cycle: GitHub sanitizes README HTML aggressively. No `<style>` blocks,
no inline `style=` for backgrounds/gradients/fonts, no loaded CSS or custom fonts. A themed
*look* has to be baked into images (the banner, badges) — the surrounding markdown always
renders in GitHub's own light/dark chrome. Plan the design around this from the start instead
of discovering it after building something GitHub will strip.

- Profile README repo must be a **public** repo named exactly `<username>/<username>`, with a
  `README.md` at the root.
- Rendered content column is roughly 830–888px wide — size banners and images accordingly
  (2-3x for retina, e.g. ~1760px wide source).
- Badges (shields.io) are the reliable way to carry color/brand — they're just images, so
  GitHub's markdown sanitizer doesn't touch them. Use them for a stack row and/or headline
  pills rather than fighting the sanitizer with raw HTML.
- Links live in two places, not one: the README body itself, AND GitHub's native
  `user/social_accounts` API/profile settings (a separate sidebar widget). Check what's
  already registered before assuming a link needs adding to either.
- Pinned repositories need at least one real public repo to point at — if everything is
  private, "the profile looks bare" is often structural, not cosmetic. Say so, and offer
  starting a small public showcase repo as the actual fix, rather than trying to visually
  compensate for having nothing to pin.
- **Don't reach for a raw `<table>` for a side-by-side layout.** GitHub's markdown CSS applies
  its default borders/row-striping to any `<table>`/`<td>` regardless of a `border="0"`
  attribute — it renders as a data table, not a clean two-column layout, and inline `style=`
  can't override it (stripped). For "image beside text" (a badge row, bullet list, avatar/mark
  next to copy), use a floated image instead: `<img src="..." align="right" width="280" />`
  followed later by `<br clear="right" />` once the next section should go back to full width.
  Both `align` and `<br clear="...">` survive GitHub's sanitizer.
- **`<video>` tags are stripped entirely** — there is no way to get a native, autoplaying video
  element in a repo README, in any form. Animated content has to be a GIF (autoplays, loops,
  but is necessarily silent — GIF has no audio track) or a static image. The only way to get a
  real inline *clickable* video player with audio is dragging the file into a GitHub issue or
  PR comment box, which mints a `github.com/user-attachments/assets/{uuid}` URL the renderer
  allow-lists specially — but that's a manual browser drag-and-drop step (not scriptable via
  `gh`/the API), and even then it's click-to-play, not autoplay (no browser allows unmuted
  autoplay, which no GitHub-side trick changes). Set expectations accordingly before generating
  an animation with sound and assuming it'll play itself on the profile.
- When unsure whether some HTML construct will survive, verify against the real renderer
  instead of guessing: `gh api -X POST /markdown -f text="$(cat README.md)" -f mode=gfm -f
  context=<owner>/<repo>` and grep the output for the tag/attribute in question.

## 4. Banner/logo generation, if pursuing one

- Ask what the mark should mean before generating — don't guess at symbolism. A generic
  "AI circuit board" or "robot" motif is the default an image model reaches for; a mark tied
  to something concrete about the person (their actual work, their region, an existing brand
  element already on their site) reads as intentional instead of stock.
- Iterate by actually looking at each generation — render it, view it, judge it against the
  brief — rather than assuming a prompt worked. Models frequently ignore precise spatial
  instructions (aspect ratio, negative space, crossing counts); if a specific model isn't
  complying after a clear prompt rewrite, try a different model rather than repeating the same
  prompt with more emphasis.
- If the mark might become a favicon (not just a banner decoration), design for that from the
  start: flat solid colors, no gradients, clean crossings, generous margin. Test the actual
  target sizes (32/48/64px, not just a large preview) with a real nearest-neighbor downscale —
  a smooth preview at 800px does not tell you how it looks at 32px.
- For a true vector favicon/logo (recommended over raster if feasible): trace the approved
  raster with `potrace` — split into one binary mask per flat color (`-fuzz` color match +
  morphological open/close to remove JPEG-noise speckles), trace each mask to SVG separately,
  recombine with the *exact* brand hex values as fills (not the JPEG-drifted sampled colors).
  This produces a genuinely scale-free asset instead of fighting raster downscale artifacts.

## 5. Animating a mark or avatar, if pursuing one

Turning a static brand mark or avatar into a short looping GIF is a reasonable ask (a
subtle motion element reads as more alive than a static badge row) but has its own
failure modes distinct from static generation:

- **Anchor on the real source image — don't describe the same motif in a fresh text
  prompt.** A blind text-only prompt reliably drifts into generic AI-video defaults (3D
  shading, gradients, an unrelated shape) even when explicitly told to stay flat/2D and
  match specific brand colors. Conditioning the generation on the actual existing asset
  (image-to-video, or a model's dedicated reference/asset-image feature) keeps the output
  on-brand far more reliably than emphasis or re-wording ever does.
- **Prefer a model's explicit subject-preservation feature over a generic image-to-video
  task, when both are available.** Some models (e.g. Veo's `VideoGenerationReferenceImage`
  with `reference_type="asset"`) are purpose-built to keep a character or mark's appearance
  intact across generated motion; a plain "animate this image" task on a different model can
  still drift the framing, crop margin, or fine detail even when it gets the subject roughly
  right. If a cheaper/faster model isn't holding the subject and framing after a clear prompt
  rewrite, switching models is usually faster than more prompt tuning.
- **Demand margin explicitly, and verify it across the whole clip, not just the first
  frame.** State plainly that nothing may touch or cross any frame edge "even at the widest
  point of motion" — then actually pull sample frames spanning the full duration (not just
  frame 0) and check containment at the frame where the animated element extends furthest.
  That peak-extent frame, not the resting pose, is where clipping actually shows up.
- **Check for an easy loop before reaching for a harder one.** If the first and last frames
  of a generated clip already closely match, a straight forward loop is clean and half the
  file size of the alternative. If they don't match, ping-pong it (reverse the clip and
  concatenate forward+reverse) rather than trying to prompt a model into a perfect loop — it
  guarantees seamlessness from a single generation, at the cost of doubling duration/file size.
- **Keep the GIF lean.** An unoptimized full-duration, full-resolution, high-fps GIF can land
  10–17MB, which is a real load-time cost on a profile page every visitor hits. Trim to a few
  seconds, ~12–15fps, a modest width (400–500px is plenty for a corner/column element), and a
  capped color palette (`palettegen`/`paletteuse` with `max_colors` and `stats_mode=diff` in
  ffmpeg) — a tuned version usually lands 3–4MB with no visible quality loss for this use case.
- **If the model generates real audio, keep the source video even though only a silent GIF
  gets embedded.** GIF can't carry an audio track at all, and (per section 3) GitHub can't
  autoplay a `<video>` element regardless. Store the original alongside the GIF in the repo's
  assets for potential reuse elsewhere later, rather than discarding it.
- **Write down what was tried, including what was rejected and why**, in a sibling
  provenance doc (e.g. `assets/banner-prompt.md`) alongside the shipped assets — model used,
  exact prompt, what the first attempt got wrong and what fixed it. A generic-looking first
  result and a subject/margin fix on the second attempt are both worth recording, so a future
  pass on the same profile doesn't blindly repeat a failed direction.

## 6. Assemble

Typical shape, adapt to what step 0 actually surfaced about the person:

```
[banner image]
[headline badge row — role/credentials]
[1-2 sentence bio grounded in their real background, not generic]
[3-5 bullets: what they're actually doing now, specific not vague]
### Stack
[shields.io badge row]
[footer: site link · social links not already covered by native social_accounts]
```

## 7. Ship

- Show the assembled README before pushing — this is public-facing content, not a private
  scratch file.
- Push to the `<username>/<username>` repo. If a showcase repo was also built, push that too
  and remind the user pinning repos to the profile is currently a manual step in GitHub's UI
  (Settings → Profile → "Customize your pins") — there is no reliable public API for it as of
  this skill being written; re-verify if attempting to automate it.
- Verify live via the API (`gh api repos/<username>/<username>/contents/README.md`), not just
  by trusting the push succeeded.

## Reference material

- Gallery of real profile README examples for design inspiration:
  https://zzetao.github.io/awesome-github-profile/
- Profile README rendered-width research: https://wh0.github.io/2025/05/18/banner-width.html
- These are starting points, not a substitute for a fresh look — profile design trends move;
  do a quick current search rather than assuming these are still the best references.
