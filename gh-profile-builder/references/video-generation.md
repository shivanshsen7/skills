# Animating a mark or avatar

Step 5 of the main workflow, if pursuing an animated element. Turning a static brand
mark or avatar into a short looping GIF is a reasonable ask (a subtle motion element
reads as more alive than a static badge row) but has its own failure modes distinct from
static generation:

- **Anchor on the real source image — don't describe the same motif in a fresh text
  prompt.** A blind text-only prompt reliably drifts into generic AI-video defaults (3D
  shading, gradients, an unrelated shape) even when explicitly told to stay flat/2D and
  match specific brand colors. Conditioning the generation on the actual existing asset
  (image-to-video, or a model's dedicated reference/asset-image feature) keeps the
  output on-brand far more reliably than emphasis or re-wording ever does.
- **Prefer a model's explicit subject-preservation feature over a generic
  image-to-video task, when both are available.** Some models (e.g. Veo's
  `VideoGenerationReferenceImage` with `reference_type="asset"`) are purpose-built to
  keep a character or mark's appearance intact across generated motion; a plain
  "animate this image" task on a different model can still drift the framing, crop
  margin, or fine detail even when it gets the subject roughly right. If a
  cheaper/faster model isn't holding the subject and framing after a clear prompt
  rewrite, switching models is usually faster than more prompt tuning.
- **Demand margin explicitly, and verify it across the whole clip, not just the first
  frame.** State plainly that nothing may touch or cross any frame edge "even at the
  widest point of motion" — then actually pull sample frames spanning the full duration
  (not just frame 0) and check containment at the frame where the animated element
  extends furthest. That peak-extent frame, not the resting pose, is where clipping
  actually shows up.
- **Check for an easy loop before reaching for a harder one.** If the first and last
  frames of a generated clip already closely match, a straight forward loop is clean
  and half the file size of the alternative. If they don't match, ping-pong it (reverse
  the clip and concatenate forward+reverse) rather than trying to prompt a model into a
  perfect loop — it guarantees seamlessness from a single generation, at the cost of
  doubling duration/file size.
- **Keep the GIF lean.** An unoptimized full-duration, full-resolution, high-fps GIF
  can land 10–17MB, which is a real load-time cost on a profile page every visitor hits.
  Trim to a few seconds, ~12–15fps, a modest width (400–500px is plenty for a
  corner/column element), and a capped color palette (`palettegen`/`paletteuse` with
  `max_colors` and `stats_mode=diff` in ffmpeg) — a tuned version usually lands 3–4MB
  with no visible quality loss for this use case.
- **If the model generates real audio, keep the source video even though only a
  silent GIF gets embedded.** GIF can't carry an audio track at all, and (see
  `github-rendering.md`) GitHub can't autoplay a `<video>` element regardless. Store
  the original alongside the GIF in the repo's assets for potential reuse elsewhere
  later, rather than discarding it.
- **Write down what was tried, including what was rejected and why**, in a sibling
  provenance doc (e.g. `assets/banner-prompt.md`) alongside the shipped assets — model
  used, exact prompt, what the first attempt got wrong and what fixed it. A
  generic-looking first result and a subject/margin fix on the second attempt are both
  worth recording, so a future pass on the same profile doesn't blindly repeat a failed
  direction.
