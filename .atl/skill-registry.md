# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| update vault | update-vault | /Users/marioinostroza/.claude/skills/update-vault/SKILL.md |
| judgment day | judgment-day | /Users/marioinostroza/.claude/skills/judgment-day/SKILL.md |
| issue creation | issue-creation | /Users/marioinostroza/.claude/skills/issue-creation/SKILL.md |

## Compact Rules

### update-vault
- Always verify file existence before writing to avoid duplicates.
- Use 'append' for logs/diaries; 'create' only for new notes with frontmatter.
- Follow folder structure in Proyectos/ (00_Diario, 01_Examya, etc.).
- Maintain mandatory YAML frontmatter (proyecto, tipo, fecha, tags).

### judgment-day
- Parallel blind review with two independent sub-agents.
- Orchestrator synthesizes confirmed vs suspect findings.
- Re-judgment required after fixes if CRITICAL issues were found.

### issue-creation
- Use templates for bug reports or feature requests.
- Every issue needs a title in conventional commit style.
- Link to relevant code or previous discussions.

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| CLAUDE.md | CLAUDE.md | Project overview, commands, and data schema |
