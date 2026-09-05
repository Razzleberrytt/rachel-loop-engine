# Rachel Loop Engine

A retention-first short-form video system for turning Rachel's raw vertical footage into polished, natural, replay-friendly social videos.

## One-line goal

`private raw video -> understand -> A/B/C edits -> QC -> loop if earned -> review renders -> learn`

## v0.6 status

The repository now contains the creative brain **and** a restart-safe one-input orchestration primitive. The core connected Descript path has been smoke-tested live with synthetic media.

### Implemented

- Rachel-specific style, retention, loop, and truthfulness rules
- durable job/variant/artifact/QC manifests
- Descript import → async wait → agent → inspect → publish adapter
- canonical `00 Raw`, `A Natural`, `B Retention`, `C Loop`
- actual composition-ID discovery instead of guessing
- idempotent resume behavior for projects, variants, and renders
- structured media-aware QC with fail-closed JSON parsing
- QC mutation fingerprint guard
- automatic strongest-passing-variant recommendation
- persisted `rle review-card job.json`
- `full_treatment()` with **QC before render**
- render only passing variants; no passing variant means no render
- analytics/learning foundation with conservative evidence gates
- Python 3.11/3.12 CI
- live synthetic verification of URL import, A/B/C creation, inspection, render, and QC contract

## Creative constitution

1. Authenticity beats generic influencer editing.
2. Retention per edit beats maximum editing.
3. A loop is optional and must earn its place.
4. Reordering must remain materially truthful.
5. The first and last seconds are both retention surfaces.
6. Failed QC cannot be overruled by a flashy/high overall score.
7. Rachel-specific evidence outranks generic social-media folklore.
8. One viral video is a hypothesis, not a permanent rule.

## Current private-media intake

For Rachel's real footage, use a **private Drive/Dropbox/direct-access URL** supported by Descript. Direct chat-attachment upload is tracked in issue #1: Descript's signed upload handshake works, but this execution environment cannot perform the required external byte `PUT`.

**Never use a public Git repository as transport for Rachel/family footage.**

## Default deliverables

- 9:16, 1080x1920, 30 fps unless source constraints require otherwise
- natural dialogue cleanup
- readable phrase-based captions
- A Natural
- B Retention
- C Loop only when it passes loop/truthfulness QC
- unlisted review renders before intentional social posting
- concise review card + recommendation

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest

rle new-job "https://example.com/private-source.mp4" --duration 32.5 --premise "family reaction" --out job.json
rle dry-run job.json
rle review-card job.json
```

## Key docs

- `WORKFLOW.md` — creative operating procedure
- `RACHEL_STYLE.md` — Rachel-specific editing voice
- `LOOP_PLAYBOOK.md` — loop selection/construction
- `QUALITY_CONTROL.md` — creative QC
- `docs/LIVE_INTEGRATION_REPORT.md` — real connector validation
- `docs/MEDIA_QC.md` — structured finished-video reviewer
- `docs/FULL_TREATMENT.md` — canonical one-input transaction
- `docs/MILESTONES.md` — current implementation gates

## Next highest-ROI gate

Run issue #2: one **real Rachel clip from a private supported URL** through `full_treatment()`, inspect the actual A/B/C behavior, and calibrate prompts/style from evidence.
