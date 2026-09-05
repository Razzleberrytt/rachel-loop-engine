# Rachel Loop Engine

A retention-first short-form video system for turning Rachel's raw vertical footage into polished, natural, replay-friendly social videos — and then learning from what actually happens after posting.

## One-line goal

`private raw video -> understand -> reviewable EDL -> zero-credit A/B/C renders -> QC -> loop if earned -> post -> capture metrics -> learn`

## v0.8 status — the post-performance learning loop is now durable

The engine already separated creative reasoning from mechanical rendering in v0.7. Version 0.8 closes the next major gap: **real post analytics can now be captured as append-only evidence instead of living only in screenshots or chat history.**

### Default architecture

`analysis -> timestamp/EDL decisions -> deterministic validation -> FFmpeg render -> QC -> post -> timestamped performance snapshots -> evidence gate`

Descript remains an **optional adapter/review surface**, not the canonical renderer.

### Implemented

- Rachel-specific style, retention, loop, and truthfulness rules
- durable job/variant/artifact/QC manifests
- portable deterministic edit-decision lists (`LocalEditPlan` / `Segment`)
- deterministic A Natural / B Retention / C Loop planning
- removal-range merging and auditable retained-source intervals
- cyclic timeline rotation around a loop anchor
- hard `loop_seam_is_source_contiguous()` QC for rotation loops
- FFmpeg execution through shell-free argv commands
- 9:16 scale/crop, 30 fps normalization, H.264/AAC export, loudness normalization
- `rle plan-local` and `rle render-local`
- local rerenders that require **no Descript AI-agent credits**
- Descript import/agent/inspect/publish adapter remains available when deliberately wanted
- structured media-aware QC and recommendation framework
- append-only performance snapshots with derived retention/engagement metrics
- direct support for replay-heavy average percentage viewed above 100%
- `rle record-metrics` with decimal or percent input (`2.15` or `215%`)
- conservative evidence-promotion gates so one viral post does not become fake certainty
- Python 3.11/3.12 CI
- live real-footage intake and deterministic render proof

## Creative constitution

1. Authenticity beats generic influencer editing.
2. Retention per edit beats maximum editing.
3. A loop is optional and must earn its place.
4. Reordering must remain materially truthful.
5. The first and last seconds are both retention surfaces.
6. Failed QC cannot be overruled by a flashy/high overall score.
7. Rachel-specific evidence outranks generic social-media folklore.
8. One viral video is a hypothesis, not a permanent rule.
9. **AI may choose timestamps; AI does not need to execute timestamps.**
10. Mechanical rerenders should be deterministic and cheap.
11. Analytics history is append-only; never erase an earlier snapshot with a later one.
12. Replay-heavy APV may legitimately exceed 100%; never cap it at 1.0.

## Real-footage calibration

The first real Rachel footage proved the private intake path and exposed editor-agent credits as the wrong execution dependency. The architecture pivoted to deterministic FFmpeg rendering in v0.7.

The current calibration clip is tracked as `RLE-2026-09-05-001`: a ~5.87 second curiosity-led baby tracking clip with a strong hidden visual restart. Its seam and text timing passed creative QC and the `C Loop` cut is the keeper. Performance evidence is intentionally still marked pending until platform analytics are captured.

See:
- `docs/ZERO_CREDIT_RENDERING.md`
- `experiments/experiment-log.md`
- `analytics/metrics-schema.md`

## Private-media intake

Chat attachments can be copied into the Rachel Loop Engine intake flow and staged through connector-managed media transport. Family footage must never be put in a public Git repository merely to make it fetchable.

Git stores code, rules, plans, schemas, experiment metadata, and anonymized learnings — **not raw family media or full-resolution exports**.

## Default deliverables

- 9:16, 1080x1920, 30 fps unless source constraints require otherwise
- natural dialogue/laughter preserved
- conservative loudness cleanup
- captions only when they improve comprehension rather than clutter the moment
- A Natural
- B Retention
- C Loop only when loop/truthfulness QC passes
- deterministic local review renders by default
- concise recommendation and experiment metadata
- timestamped analytics snapshots after posting

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest

rle new-job "https://example.com/private-source.mp4" --duration 37.97 --premise "family reaction" --out job.json

# Create auditable local A/B/C plans. These timestamps are examples.
rle plan-local job.json \
  --remove 12.15:19.80 \
  --head-trim 1.70 \
  --loop-anchor 31.00 \
  --out-dir local-plans

# Render without editor AI credits.
rle render-local job.json local-plans/loop.json ./raw.mp4 --out ./C_Loop.mp4

# After posting, append analytics without overwriting earlier snapshots.
rle record-metrics job.json \
  --platform youtube_shorts \
  --variant "C Loop" \
  --views 2500 \
  --apv 215% \
  --likes 100 \
  --shares 25
```

## Key docs

- `WORKFLOW.md` — creative operating procedure
- `RACHEL_STYLE.md` — Rachel-specific editing voice
- `LOOP_PLAYBOOK.md` — loop selection/construction
- `QUALITY_CONTROL.md` — creative QC
- `docs/ZERO_CREDIT_RENDERING.md` — default deterministic execution architecture
- `docs/LIVE_INTEGRATION_REPORT.md` — connector validation
- `docs/MEDIA_QC.md` — structured finished-video reviewer
- `docs/FULL_TREATMENT.md` — one-input transaction design
- `docs/MILESTONES.md` — current implementation gates
- `analytics/metrics-schema.md` — append-only post-performance schema

## Next highest-ROI gate

Collect multiple timestamped performance snapshots from real Rachel posts, starting with `RLE-2026-09-05-001`, then compare repeated loop/non-loop patterns before promoting any hypothesis into a permanent Rachel rule.
