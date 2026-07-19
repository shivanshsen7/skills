# Repo conventions

This repo holds one person's own Claude Code skills, published individually as each is
vetted for public sharing — not a batch dump of everything in a local `.claude/skills/`
directory. A skill only lands here once it's been checked for third-party origin markers,
secrets/leakage, and any employer/publishing-consent constraint, and the user has
explicitly confirmed it. Don't add a skill here just because it exists locally.

## Structure

Each skill lives at `skills/<name>/`, containing `SKILL.md` and, if the skill has enough
procedural detail to make one file unwieldy, a `references/<topic>.md` per distinct area
(e.g. `references/video-generation.md`, not one long file covering everything). Keep
`SKILL.md` itself to a lean process outline — a numbered/bulleted workflow with pointers
into `references/` for the "how exactly" — rather than inlining every detail. If a skill
is genuinely simple enough to fit in ~50 lines with no split needed, that's fine too; don't
force a references/ folder that isn't earning its keep.

## Adding a skill

Update the table in `README.md` with a one-line description, and keep this file's
structure guidance in sync if the convention changes. No versioning/changeset tooling or
plugin marketplace packaging yet — revisit that once there are several skills shipping in
parallel; for one or two skills it's overhead without a payoff.
