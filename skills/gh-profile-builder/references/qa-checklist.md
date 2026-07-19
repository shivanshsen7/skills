# Pre-publish QA checklist

Referenced from step 7 (Ship). Verifying by inspection beats trusting a step "should"
have worked — every item below is a real failure mode this skill has hit in practice.

- **Secrets/attribution scan** (see `vetting.md`): grep everything going public for API
  keys, internal hostnames, local file paths, employer names, and third-party origin
  markers before it ships — not after.
- **Rendering survives the sanitizer** (see `github-rendering.md`): don't assume an
  HTML construct (a float, a `<br clear>`, an attribute) renders the way it does in a
  browser preview. Check the real output:
  `gh api -X POST /markdown -f text="$(cat README.md)" -f mode=gfm -f context=<owner>/<repo>`
  and grep for the tag/attribute in question.
- **Generated images, viewed at actual size** (see `asset-generation.md`): a smooth
  800px preview does not tell you how a mark looks at favicon size. Render the real
  target sizes (32/48/64px) with a real nearest-neighbor downscale before approving.
- **Generated video, sampled across the full clip** (see `video-generation.md`): pull
  frames spanning the entire duration, not just frame 0 — check containment at the
  frame where motion extends furthest, since that's where clipping actually shows up.
  Check whether first/last frames already match before ping-ponging a loop.
- **Show the assembled README before pushing.** This is public-facing content, not a
  private scratch file — the user should see the real thing before it goes live, not a
  description of it.
- **Verify live after pushing, not just that the push succeeded**:
  `gh api repos/<username>/<username>/contents/README.md` (and spot-check any new
  asset URLs resolve, e.g. `curl -sI https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`).
