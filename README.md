# Rachel Loop Engine

A retention-first short-form video system for turning Rachel's raw vertical footage into polished, natural, replay-friendly social videos.

## One-line goal

`private raw video -> understand -> A/B/C edits -> loop if earned -> QC -> review renders -> learn`

## v0.5 status

This is now more than an editing playbook. The repository contains an executable, restart-safe orchestration foundation and its core Descript path has been smoke-tested live with synthetic media.

### Implemented

- Rachel-specific creative constitution and style rules
- retention + loop playbooks
- durable source/job/variant/artifact/QC models
- complete JSON job manifests
- deterministic plan validation
- transport-neutral editor interface
- Descript import → wait → agent → inspect → publish coordinator
- canonical compositions:
  - `00 Raw`
  - `A Natural`
  - `B Retention`
  - `C Loop`
- real composition-ID discovery instead of guessing
- idempotent resume behavior that reuses existing projects/variants/renders
- mock Descript transport for offline tests
- CLI (`rle`)
- machine-readable job schema
- conservative analytics-learning foundation
- Python 3.11/3.12 CI
- live URL-based Descript integration verification
- structured non-mutating media-aware QC
- automatic variant recommendation + persisted review card

## Creative constitution

1. Authenticity beats generic influencer editing.
2. Retention per edit beats maximum editing.
3. A loop is used only when it improves the video.
4. The strongest moment may become the opening when that is truthful and clearer.
5. The final second matters as much as the first.
6. Every published video is an experiment.
7. Rachel-specific evidence outranks generic advice.
8. Never optimize metrics by making content materially misleading.

## Default output

- 9:16 vertical
- 1080x1920
- 30 fps unless source/platform requires otherwise
- captions enabled
- natural dialogue cleanup
- no forced CTA that harms the ending
- meaningful variants only:
  - **A — Natural**
  - **B — Retention**
  - **C — Loop**

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest

rle new-job "https://example.com/private-source.mp4" --duration 32.5 --premise "family reaction" --out job.json
rle dry-run job.json
```

## Live integration status

The URL-based connected Descript path has been verified end-to-end using synthetic media:

`URL import -> async wait -> 00 Raw -> agent -> A/B/C -> inspect -> UUID resolution -> 1080p unlisted render`

Direct chat-attachment upload is not yet end-to-end in this execution environment: Descript returns the correct signed upload slot, but the current container cannot perform the external byte `PUT`. For Rachel's private footage, use a supported private Drive/Dropbox/direct-access URL until that byte bridge is added.

**Never put private Rachel/family raw footage in this Git repository.**

## Repository map

- `AGENTS.md` — AI-agent non-negotiables
- `WORKFLOW.md` — end-to-end operating procedure
- `RACHEL_STYLE.md` — Rachel-specific editing voice
- `RETENTION_RULES.md` — retention heuristics
- `LOOP_PLAYBOOK.md` — loop construction/selection
- `QUALITY_CONTROL.md` — pre-render QC
- `architecture/PIPELINE.md` — technical architecture
- `prompts/` — versioned editor prompts
- `config/` — machine-readable defaults/learning gates
- `analytics/` — measurement definitions and learned rules
- `experiments/` — hypotheses and promoted winners
- `docs/LIVE_INTEGRATION_REPORT.md` — real connector validation
- `docs/MEDIA_QC.md` — structured finished-video review contract
- `src/rachel_loop_engine/` — executable engine
- `tests/` — deterministic tests

## Next highest-ROI gate

Run the first **real Rachel clip from a private supported URL**, inspect all three edits, score the loop seam and story truthfulness, then feed those observations back into `RACHEL_STYLE.md` and the prompt set.
