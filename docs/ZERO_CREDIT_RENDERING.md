# Zero-Credit Rendering

## Decision

Rachel Loop Engine must not depend on an editor AI agent for mechanical editing or rerenders.

The default execution path is now:

`private source -> analysis -> timestamp/EDL decisions -> deterministic validation -> FFmpeg render -> QC -> analytics`

Descript remains an **optional adapter/review surface**, not the canonical renderer.

## Why

A live real-footage calibration proved that editor-agent credits can be exhausted during a single multi-variant pass. Mechanical operations such as trim, reorder, concat, crop, scale, loudness normalization, and rerendering do not require repeated AI reasoning.

The expensive reasoning step should produce a small, reviewable edit decision list (EDL). Once the EDL exists, rendering it should be deterministic and repeatable at effectively zero marginal AI-credit cost.

## Core rule

**AI may choose timestamps. AI does not need to execute timestamps.**

A reviewed plan is the source of truth for:

- source intervals retained/removed
- variant ordering
- loop anchor
- crop/zoom intent
- output dimensions and frame rate
- audio normalization target

The FFmpeg adapter executes that plan exactly.

## Loop edge: cyclic timeline rotation

When a useful loop anchor lies inside retained footage, rotate the retained EDL around that source timestamp.

If the first retained segment starts at the anchor and the last retained segment ends at the same anchor, the replay boundary reconnects two adjacent source moments. This is stronger than trying to disguise a random seam with a crossfade.

The engine exposes `loop_seam_is_source_contiguous()` as a hard, deterministic QC property for this loop type.

## Credit policy

1. Do not invoke Descript AI for ordinary trimming, reordering, scaling, audio leveling, or rerendering.
2. Prefer deterministic local renders for A/B/C once timestamps are known.
3. Use editor AI only when a capability genuinely requires it and the user wants that tradeoff.
4. A credit failure must degrade to local execution, never block the job.
5. Store plans/manifests, not raw family media, in Git.
6. Keep Rachel Loop Engine completely separate from unrelated projects and repositories.

## First real-footage proof

The first real calibration clip successfully moved from a ChatGPT attachment through private staging into the editing workflow. The editor-agent pass created A/B/C compositions but then stopped on AI-credit exhaustion.

The same source was then rendered locally with a deterministic loop EDL. The upgraded loop used a source-contiguous anchor and passed a full FFmpeg decode check. This validates the architectural pivot: creative analysis can be separated from media execution.
