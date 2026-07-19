---
name: create-carousel
description: Create LinkedIn carousel slides as HTML + export to PDF using Playwright. Use when the user asks to create a carousel, LinkedIn slides, slide deck, or swipeable content for social media.
---

# Create LinkedIn Carousel

Generate carousel slides as HTML, then export to PDF for LinkedIn upload.

## Files

- **Template:** Read `scripts/template.html` for the base HTML with design tokens, styles, dark slide support
- **Export script:** Run `scripts/export-carousel.mjs` to convert HTML → PDF via Playwright

## Design Tokens

Primary: #A82E4B | Bright (dark slides): #E04466 | Background: #FAFAF8 | Text: #2F2F31
Fonts: DM Serif Display (headings), DM Sans (body), JetBrains Mono (labels)

## Rules

**Sizing:**
- 1080x1080px square slides, 48px/56px padding
- Min font: headings 56px+, body 26px+, labels 20px+, watermark/numbers 24px
- Must be readable at ~375px phone width

**Structure:**
- 6-8 slides. One idea per slide.
- Every slide: `.slide-number` (bottom right) + `.watermark` (bottom left)
- Slide 1: include `swipe >` cue at bottom center
- Dark slides: add `class="dark"`, use `--primary-bright` not `--primary`

**Content:**
- Hook first, CTA last ("Link in comments")
- Stats/numbers get their own slide
- Alternate light/dark for rhythm
- Verify all claims against sources before including

## Workflow

1. Read `scripts/template.html` — copy and adapt for the topic
2. Save HTML to the target location
3. Preview and iterate
4. Export to PDF:
   ```bash
   cd /tmp && npm install playwright 2>/dev/null
   node ~/.claude/skills/create-carousel/scripts/export-carousel.mjs <html-path> <pdf-path>
   # optional 3rd arg for photo-heavy carousels landing too large:
   node ~/.claude/skills/create-carousel/scripts/export-carousel.mjs <html-path> <pdf-path> jpeg:95
   ```
   Requires: `npx playwright install chromium` (one-time). Default export is
   lossless PNG — see "File size" below before reaching for the `jpeg:` option.

## Photo carousels (real photos, not text/data slides)

The template above was built for text/data slides; a carousel built from real
photos (event recap, people, etc.) needs a few extra rules the template
doesn't enforce for you:

- **Embed photos as base64 data URIs** directly in the `<img>`/background —
  keeps the HTML self-contained and portable.
- **Never upscale a source photo to "normalize" sizes.** Resize commands like
  ImageMagick's `-resize 1600x1600>` only shrink (the `>` means "only if
  larger") — if you see an embedded image *larger* than its source file, a
  wrong/duplicate file got used, or an explicit `!` force-resize crept in.
  Upscaling via plain resize adds blur, not detail — verify by decoding the
  actual embedded dimensions and diffing against the source, don't trust
  chained agent hand-offs blindly.
- **Don't recompress a JPEG source at a *lower* quality than it likely
  already has**, especially anything sent through WhatsApp — WhatsApp already
  compresses aggressively. A second lossy pass compounds artifacts for no
  benefit. Prefer `-strip` (EXIF only, no requality) or a high requality
  (`-quality 95`+) if resizing is genuinely needed.
- **`object-fit: cover` on a 1:1 slide will crop group photos** — a wide
  group photo cropped into a square can cut people off at the edges. Check
  the actual rendered output (read the exported PDF page back, don't assume),
  and if someone's cut off, adjust `object-position` (shift toward the side
  being lost, e.g. `object-position: 68% center` to reveal more of the right
  edge) — small percentage nudges, re-export, re-check.
- **A camera-native photo (HEIC/JPEG straight off a phone) has real detail —
  don't crush it to the same small cap as a WhatsApp-compressed photo.**
  Resize camera-native sources to ~2400px long edge, not 1600px; WhatsApp
  sources are already capped by WhatsApp's own compression regardless of
  what you do locally, so there's a real ceiling there that no local
  resize/requality changes.
- **If a WhatsApp-sourced photo still looks soft/blocky after the above**,
  a local Real-ESRGAN pass (faithful GAN restoration, not generative) can
  meaningfully clean up compression artifacts without altering faces —
  a from-scratch RRDBNet + public `RealESRGAN_x4plus.pth` weights, no
  `basicsr` package needed (it's unmaintained and breaks on current Python —
  fails on `setup.py`'s version-string read; don't fight it, reimplement the
  ~80-line architecture directly). Avoid diffusion/generative "AI upscalers"
  (Gemini, Flux-based enhancers, anything marketed as "creative" or
  "face-optimized") on real identifiable people's photos — those regenerate
  detail rather than restore it, which can drift someone's actual likeness.
  Faithful beats generative for real people, regardless of brand.

## File size

LinkedIn's real limit is **100MB and 300 pages** — the guidance below is a
soft target for fast mobile loading, not a hard constraint. Don't degrade
visual quality chasing an arbitrary small number if the content genuinely
needs it (a photo-heavy carousel is legitimately larger than a text one).

- Text/data slides: PNG (default) stays small naturally — vector-ish content
  compresses well losslessly. No reason to ever use JPEG here.
- Photo-heavy slides: PNG is lossless but can land 40MB+ for 6-8 full-bleed
  photos — that's fine, still well under LinkedIn's cap. Only switch to
  `jpeg:<quality>` (quality **95 or higher**, never lower — anything below
  visibly degrades faces and small text, which defeats the point) if you
  want a smaller file and the loss is genuinely negligible at that quality.
- A rough soft target for quick loading: keep it under ~10-15MB where
  quality permits, but treat that as a nice-to-have, not a gate.

## Checklist

- [ ] Claims fact-checked
- [ ] Names spelled correctly
- [ ] Slide numbers sequential
- [ ] Dark slides use --primary-bright
- [ ] Text readable at phone size
- [ ] Swipe cue on slide 1
- [ ] Watermark on every slide
- [ ] File size reasonable for content (see "File size" — not a hard 10MB gate)
- [ ] For photo carousels: nobody cropped out mid-body, no upscale-blur, no
      double JPEG compression
