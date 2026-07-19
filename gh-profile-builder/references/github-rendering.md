# GitHub's actual rendering constraints

Step 3 of the main workflow. GitHub sanitizes README HTML aggressively. No `<style>`
blocks, no inline `style=` for backgrounds/gradients/fonts, no loaded CSS or custom
fonts. A themed *look* has to be baked into images (the banner, badges) — the
surrounding markdown always renders in GitHub's own light/dark chrome. Plan the design
around this from the start instead of discovering it after building something GitHub
will strip.

- Profile README repo must be a **public** repo named exactly `<username>/<username>`,
  with a `README.md` at the root.
- Rendered content column is roughly 830–888px wide — size banners and images
  accordingly (2-3x for retina, e.g. ~1760px wide source).
- Badges (shields.io) are the reliable way to carry color/brand — they're just images,
  so GitHub's markdown sanitizer doesn't touch them. Use them for a stack row and/or
  headline pills rather than fighting the sanitizer with raw HTML.
- Links live in two places, not one: the README body itself, AND GitHub's native
  `user/social_accounts` API/profile settings (a separate sidebar widget). Check what's
  already registered before assuming a link needs adding to either.
- Pinned repositories need at least one real public repo to point at — if everything is
  private, "the profile looks bare" is often structural, not cosmetic. Say so, and offer
  starting a small public showcase repo as the actual fix, rather than trying to
  visually compensate for having nothing to pin.
- **Don't reach for a raw `<table>` for a side-by-side layout.** GitHub's markdown CSS
  applies its default borders/row-striping to any `<table>`/`<td>` regardless of a
  `border="0"` attribute — it renders as a data table, not a clean two-column layout,
  and inline `style=` can't override it (stripped). For "image beside text" (a badge
  row, bullet list, avatar/mark next to copy), use a floated image instead:
  `<img src="..." align="right" width="280" />` followed later by
  `<br clear="right" />` once the next section should go back to full width. Both
  `align` and `<br clear="...">` survive GitHub's sanitizer.
- **`<video>` tags are stripped entirely** — there is no way to get a native,
  autoplaying video element in a repo README, in any form. Animated content has to be a
  GIF (autoplays, loops, but is necessarily silent — GIF has no audio track) or a static
  image. The only way to get a real inline *clickable* video player with audio is
  dragging the file into a GitHub issue or PR comment box, which mints a
  `github.com/user-attachments/assets/{uuid}` URL the renderer allow-lists specially —
  but that's a manual browser drag-and-drop step (not scriptable via `gh`/the API), and
  even then it's click-to-play, not autoplay (no browser allows unmuted autoplay, which
  no GitHub-side trick changes). Set expectations accordingly before generating an
  animation with sound and assuming it'll play itself on the profile.
- When unsure whether some HTML construct will survive, verify against the real
  renderer instead of guessing:
  `gh api -X POST /markdown -f text="$(cat README.md)" -f mode=gfm -f context=<owner>/<repo>`
  and grep the output for the tag/attribute in question.
