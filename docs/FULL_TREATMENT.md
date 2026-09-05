# Full Treatment Transaction

`DescriptWorkflowRunner.full_treatment(job)` is the canonical high-level execution primitive for the original product goal: one source in, reviewed variants out.

## Order of operations

1. Set job to `editing`.
2. Reuse or create the Descript project.
3. Reuse or create canonical A/B/C compositions.
4. Set job to `qc`.
5. Run media-aware QC against the real composition IDs.
6. Compute the recommended passing variant.
7. If **none** pass, set job to `failed` and render nothing.
8. Set job to `exporting`.
9. Render only passing variants (or only the recommended variant when configured).
10. Set job to `complete` and persist artifacts + recommendation.

## Why QC precedes rendering

Rendering is an external, asynchronous, potentially costly operation. A loop variant that fails truthfulness/seam QC should not consume render work or appear beside valid deliverables. The transaction therefore treats QC as a hard gate.

## Default behavior

`publish_all_passing=True` renders every passing variant so Rachel/Willie can compare A/B/C when they are all legitimate. `False` renders only the engine's recommended passing variant.

## Failure behavior

No passing variants is a legitimate failed job state, not an invitation to lower QC thresholds. The manifest stores `failure_reason`, and no review render is created.
