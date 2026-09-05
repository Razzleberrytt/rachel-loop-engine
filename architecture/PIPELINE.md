# Pipeline Architecture

## Principle

Rachel Loop Engine owns decisions; editor services execute them. Creative truth must not be trapped inside one vendor.

## Layers

1. **Intake** — `SourceSpec` + stable `job_id`.
2. **Analysis** — transcript, premise, moments, risks, hook/payoff candidates.
3. **Planning** — Natural/Retention/Loop intent and loop viability.
4. **Prompt composition** — merge versioned Rachel rules with runtime context.
5. **Editor adapter** — import, agent edit, inspect project, publish.
6. **QC** — deterministic manifest checks plus media-aware review.
7. **Artifacts** — composition IDs, share URLs, durations, QC state.
8. **Analytics** — observed post metrics.
9. **Learning** — conservative evidence gate before permanent rule promotion.

## State/retry model

- Do not redo successful upstream stages merely because a later stage failed.
- Persist external project/job/composition IDs as soon as they exist.
- Resolve compositions from project inspection; never fabricate IDs.
- Publish is per composition, so one failed variant does not block the others.
- Loop is optional and may be downgraded/rejected independently.

## Service boundary

`EditorTransport` is intentionally small:

- `import_media`
- `run_agent`
- `wait`
- `get_project`
- `publish`

This exactly captures what the current Descript-connected workflow needs while remaining mockable.
