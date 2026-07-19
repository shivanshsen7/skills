# Banner/logo/favicon generation

Step 4 of the main workflow, if pursuing a generated mark.

- Ask what the mark should mean before generating — don't guess at symbolism. A generic
  "AI circuit board" or "robot" motif is the default an image model reaches for; a mark
  tied to something concrete about the person (their actual work, their region, an
  existing brand element already on their site) reads as intentional instead of stock.
- Iterate by actually looking at each generation — render it, view it, judge it against
  the brief — rather than assuming a prompt worked. Models frequently ignore precise
  spatial instructions (aspect ratio, negative space, crossing counts); if a specific
  model isn't complying after a clear prompt rewrite, try a different model rather than
  repeating the same prompt with more emphasis.
- If the mark might become a favicon (not just a banner decoration), design for that
  from the start: flat solid colors, no gradients, clean crossings, generous margin.
  Test the actual target sizes (32/48/64px, not just a large preview) with a real
  nearest-neighbor downscale — a smooth preview at 800px does not tell you how it looks
  at 32px.
- For a true vector favicon/logo (recommended over raster if feasible): trace the
  approved raster with `potrace` — split into one binary mask per flat color (`-fuzz`
  color match + morphological open/close to remove JPEG-noise speckles), trace each
  mask to SVG separately, recombine with the *exact* brand hex values as fills (not the
  JPEG-drifted sampled colors). This produces a genuinely scale-free asset instead of
  fighting raster downscale artifacts.
