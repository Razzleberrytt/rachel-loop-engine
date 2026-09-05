# Media-Aware QC and Review Cards

Deterministic plan checks catch structural errors, but they cannot hear awkward audio, see a bad crop, or judge whether an actual loop seam feels natural. v0.5 adds a second QC layer that asks the editor agent to **inspect, not mutate**, each finished composition.

## Contract

The reviewer targets one real composition ID and returns a marked JSON object containing:

- `passed`
- `overall_score` (0–100 editorial quality; not an algorithm prediction)
- `story_truthfulness` (0–5)
- `hook_strength` (0–5)
- `pacing` (0–5)
- `caption_quality` (0–5 or null)
- `audio_quality` (0–5 or null)
- `loop_seam` (0–5 or null)
- warnings
- notes

The parser fails closed if the required marker/JSON contract is missing.

## Recommendation policy

Only passing variants are eligible. The highest overall editorial score wins. Exact score ties use the conservative order:

`Natural > Retention > Loop`

That tie-break prevents the system from selecting a more aggressive edit merely because it exists.

## Persistence

The full media review is stored in each `VariantArtifact.metadata["media_review"]`; the normalized pass/score/warnings also populate `VariantArtifact.qc`. The job stores `recommended_variant` in metadata.

Because artifacts now round-trip through the JSON manifest, a new session can render the same review card without rerunning AI QC.

## CLI

```bash
rle review-card job.json
```

This prints a concise operator card suitable for choosing which accepted variant to post.

## Trust boundary

The media reviewer is advisory automation, not ground truth. Manual review remains mandatory when reordering could change the meaning of a sensitive/private family moment or when the reviewer reports uncertainty.

## Mutation guard

The Descript agent may report `project_changed=true` even on an inspection prompt. The engine therefore fingerprints the targeted canonical composition before and after QC using the project-inspection surface. If the composition disappears/renames or its duration changes beyond a small tolerance, QC fails closed instead of accepting the review. The raw agent `project_changed` flag is persisted for audit.
