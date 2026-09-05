# Operator Runbook

## Standard invocation

The intended user-facing command is conceptually:

> Rachel video. Full treatment.

A bridge creates a job manifest and executes the pipeline.

## Failure rules

- Import failure: retry only the import; do not create duplicate projects blindly.
- Agent edit failure: retain project ID and retry the edit against the same project.
- Publish failure: never redo the edit just to retry rendering.
- Missing loop viability: publish Natural/Retention; Loop is optional.
- QC failure: do not silently publish. Record the reason and fall back to the strongest passing variant.
- Ambiguous premise: preserve source chronology more conservatively rather than fabricating a hook.

## Idempotency

Use `job_id` in project names and persistent metadata. Re-running a known job should reuse known project/composition IDs when possible.

## Human review gates

Require human review when:

- a child/private family moment could be interpreted differently after reordering;
- the edit changes apparent chronology in a material way;
- captions contain uncertain names/medical/legal claims;
- a loop intentionally withholds context that changes meaning;
- audio cleanup damages intelligibility.
