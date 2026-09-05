# Rachel Loop Engine

A retention-first short-form video system for turning Rachel's raw vertical footage into polished, natural, replay-friendly social videos.

## One-line goal

`raw video -> understand -> restructure -> polish -> loop if earned -> QC -> export -> learn`

## What v0.3 adds

The repository is no longer only an editing playbook. It now has an executable orchestration foundation:

- durable source/job/variant/artifact/QC models
- JSON job manifests
- deterministic plan validation
- transport-neutral editor interface
- Descript coordinator for import → agent edit → wait → inspect → publish
- named A/B/C composition workflow
- mock Descript transport for offline tests
- prompt composition
- CLI (`rle`)
- machine-readable job schema
- integration/runbook docs
- conservative analytics-learning foundation
- CI on Python 3.11 and 3.12

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
- variants when meaningfully distinct:
  - A — Natural
  - B — Retention
  - C — Loop

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest

rle new-job "https://example.com/raw.mp4" --duration 32.5 --premise "family reaction" --out job.json
rle dry-run job.json
```

## Architecture

The creative brain is service-independent. `DescriptAdapter` coordinates the editing workflow but receives an `EditorTransport` implementation. In ChatGPT, a bridge can map that transport to the connected Descript tools. Tests use a deterministic mock. A future editor can implement the same transport boundary.

See:

- `WORKFLOW.md` — creative operating procedure
- `RACHEL_STYLE.md` — Rachel-specific style
- `LOOP_PLAYBOOK.md` — loop strategies
- `QUALITY_CONTROL.md` — creative QC
- `docs/DESCRIPT_INTEGRATION.md` — live adapter contract
- `docs/RUNBOOK.md` — operational failure/retry rules
- `docs/MILESTONES.md` — implementation state
- `src/rachel_loop_engine/` — executable engine

## Current state

**M1 is complete. M2 executable orchestration foundation is complete and the M3 multi-variant coordinator is implemented against a mocked transport.** The next real-world gate is M2.5: attach the live Descript bridge and process the first raw Rachel video end-to-end.
