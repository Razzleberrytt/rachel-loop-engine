# Rachel Loop Engine

A retention-first short-form video system for turning Rachel's raw vertical footage into polished, natural, replay-friendly social videos.

## One-line goal

`private raw video -> understand -> reviewable EDL -> zero-credit A/B/C renders -> QC -> loop if earned -> learn`

## v0.7 status — deterministic rendering is now the default

The creative brain remains Rachel-specific, but the mechanical editor is no longer allowed to become a credit bottleneck.

### Default architecture

`analysis -> timestamp/EDL decisions -> deterministic validation -> FFmpeg render -> QC -> analytics`

Descript is retained as an **optional adapter/review surface**, not the canonical renderer.

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
- analytics/learning foundation with conservative evidence gates
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

## Real-footage calibration result

A real Rachel clip was uploaded directly in ChatGPT, staged without using public GitHub, and successfully imported into Descript. Descript created `00 Raw`, `A Natural`, `B Retention`, and `C Loop`, but its AI agent then stopped because the account ran out of AI credits.

That failure exposed the correct architecture: the same source was rendered outside the editor agent using a deterministic EDL and FFmpeg. The loop variant used a cyclic timeline rotation so the replay boundary reconnects the original source at the chosen loop anchor. The output passed a full decode check.

See `docs/ZERO_CREDIT_RENDERING.md`.

## Private-media intake

Chat attachments can now be copied into the Rachel Loop Engine intake flow and staged through connector-managed media transport. Family footage must never be put in a public Git repository merely to make it fetchable.

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

## Next highest-ROI gate

Run several real Rachel clips through the deterministic path, record actual performance, and use those results to improve timestamp selection and Rachel-specific rules. Descript-agent usage is no longer a prerequisite for that learning loop.
