# Vetting content before it goes public

Step 2 of the main workflow. This is the step most likely to be skipped under time
pressure, and the one with the most real cost if skipped — republishing someone else's
content as the user's own is a misattribution problem, not just a taste problem. Before
including ANY file, skill, snippet, or project in something public-facing:

- Check for third-party origin markers: an `origin:`, `author:`, `source:`, or `license:`
  field in frontmatter that names anyone other than the user; a `source: community` tag;
  body text like "curated by X" or "prompts from X". Any of these means: exclude it, or
  ask the user to confirm explicit permission/attribution before including it.
- Grep candidate content for secrets and leakage before it goes anywhere public: API
  keys, internal hostnames, other local file paths, employer names.
  (`grep -rniE "api[_-]?key\s*=\s*['\"]|sk-[a-zA-Z0-9]{20}|password\s*=\s*['\"]"` as a
  baseline pass — adapt to what the content actually is.)
- Check the user's own memory/notes for any documented employment or publishing-consent
  constraints (outside-work clauses, employer approval requirements) before publishing
  anything new publicly. If such a constraint exists, surface it and get explicit
  confirmation rather than silently proceeding — this is genuinely their call, not a
  default.
- When multiple candidate items exist (e.g. a folder of skills, projects, certifications
  to showcase), present the vetting result as a clear include/exclude list with the
  reason for each exclusion, and let the user confirm the final set rather than deciding
  unilaterally.
