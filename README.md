# Skills

A curated set of reusable AI-agent skills. Built for real use in day-to-day work, not as
demos. Currently just one skill — more get added here as they're individually vetted for
public sharing, not in a batch.

Each skill lives under `skills/<name>/` as a self-contained directory: a `SKILL.md`
(frontmatter + a lean process outline) and, where a skill has enough procedural detail to
warrant it, a `references/` subfolder of topic files the agent reads on demand rather than
loading everything up front. Written in the [Claude Code](https://claude.com/claude-code)
skill format.

## Skills

| Skill | Description |
| --- | --- |
| [`gh-profile-builder`](./skills/gh-profile-builder) | Build or upgrade a GitHub profile: the special `<username>/<username>` README repo, GitHub's native social-accounts field, and optionally a curated public showcase repo. Grounds the design in the person's actual site/work rather than running a generic Q&A template, and covers real GitHub-markdown rendering gotchas (table borders, stripped `<video>` tags) and animated-asset generation pitfalls learned from actual use. |

## Install

Three ways to get a skill from this repo, pick whichever tool you already have:

**[GitHub CLI](https://cli.github.com/manual/gh_skill_install)** (`gh skill install`):
```
gh skill install shivanshsen7/skills gh-profile-builder --agent claude-code --scope user
```
Drop `--scope user` for a project-level install instead, or omit the skill name to pick
interactively. `--agent` targets other harnesses too (`cursor`, `github-copilot`, etc.).

**[skills.sh](https://skills.sh)** (`npx`, no gh required):
```
npx skills add shivanshsen7/skills
```

**Manual copy** (no tooling): copy `skills/gh-profile-builder/` into `.claude/skills/gh-profile-builder/`
at the project level, or `~/.claude/skills/gh-profile-builder/` at the user level — the
nesting in this repo is for organization, not the install path, so it works either way.

## Requirements

Any dependencies (binaries, environment variables for API keys) are listed in the skill's
`SKILL.md` frontmatter under `metadata.requires`. Nothing here is bundled with credentials —
bring your own.

## License

No license file is included; treat this as source-available for reference. Open an issue if
you want to reuse something and licensing terms aren't clear.
