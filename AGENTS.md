# Agent Instructions — Rachel Loop Engine

## Mission

Turn raw Rachel video into authentic, retention-first short-form edits while preserving truth, family context, and an evidence-backed learning loop.

## Non-negotiables

1. Read `RACHEL_STYLE.md`, `RETENTION_RULES.md`, `LOOP_PLAYBOOK.md`, and `QUALITY_CONTROL.md` before changing creative behavior.
2. A loop is optional. Never force one to satisfy a template.
3. Do not materially misrepresent chronology, dialogue, reactions, or claims by reordering footage.
4. Rachel-specific observed evidence outranks generic social-media folklore.
5. One high-performing video is a hypothesis, not a permanent rule.
6. Keep raw video and rendered exports out of Git.
7. Keep editor/vendor calls behind adapters. Do not embed a vendor into the creative layer.
8. Do not invent undocumented APIs, composition IDs, analytics, or successful exports.
9. External operations are asynchronous: preserve IDs and retry the failed stage, not the whole pipeline.
10. Before merging code changes, run the full test suite and compile check.

## Canonical composition names

- `00 Raw`
- `A Natural`
- `B Retention`
- `C Loop`

These names are machine contracts. Change them only with matching code/tests/docs updates.

## Definition of done

A feature is not complete because a prompt sounds good. It must have, where applicable:
- typed/durable state
- failure behavior
- deterministic tests
- docs/runbook update
- no fabricated external success
