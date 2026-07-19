# Skills

A curated set of reusable AI-agent skills. Built for real use in day-to-day work, not as
demos. Currently just one skill — more get added here as they're individually vetted for
public sharing, not in a batch.

Each skill lives under `skills/<name>/` as a self-contained directory: a `SKILL.md`
(frontmatter + a lean process outline) and, where a skill has enough procedural detail to
warrant it, a `references/` subfolder of topic files the agent reads on demand rather than
loading everything up front. Written in the [Claude Code](https://claude.com/claude-code)
skill format; copy a skill directory into `.claude/skills/<name>/` (project-level) or
`~/.claude/skills/<name>/` (user-level) to install it there — the nesting here is for repo
organization, not the install path.

## Skills

| Skill | Description |
| --- | --- |
| [`gh-profile-builder`](./skills/gh-profile-builder) | Build or upgrade a GitHub profile: the special `<username>/<username>` README repo, GitHub's native social-accounts field, and optionally a curated public showcase repo. Grounds the design in the person's actual site/work rather than running a generic Q&A template, and covers real GitHub-markdown rendering gotchas (table borders, stripped `<video>` tags) and animated-asset generation pitfalls learned from actual use. |

## Requirements

Any dependencies (binaries, environment variables for API keys) are listed in the skill's
`SKILL.md` frontmatter under `metadata.requires`. Nothing here is bundled with credentials —
bring your own.

## License

No license file is included; treat this as source-available for reference. Open an issue if
you want to reuse something and licensing terms aren't clear.
