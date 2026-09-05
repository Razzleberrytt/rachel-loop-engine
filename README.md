# Rachel Loop Engine

Retention-first short-form video system for turning Rachel's private vertical footage into polished, replay-friendly, measurable experiments.

## v0.9 — Loop Intelligence Suite

`private source -> probe -> seam hunt -> hypothesis variants -> deterministic render -> mechanical QC -> fingerprint -> recommend -> post -> timestamped evidence -> matched comparison -> learn`

### What is now implemented

- Rachel-specific style, retention, truthfulness, and loop rules
- private-media-safe workflow; Git stores code/metadata, not raw family media
- deterministic FFmpeg EDL rendering with no editor AI-credit dependency
- ffprobe stream detection, including silent-video support
- automatic Seam Hunter for source-contiguous rotation anchors
- experimental visual-match pair discovery
- three-cycle loop-preview rendering
- mechanical finished-file QC: decode, duration, resolution, FPS, audio, black/freeze detection
- core A Natural / B Retention / C Loop compatibility
- hypothesis-driven compression, payoff-first, alternate-hook, no-text, and visual-match variants
- real timed FFmpeg text overlays for text/no-text experiments
- stable creative fingerprints attached to post performance
- append-only analytics with APV above 100%
- screenshot-derived analytics provenance with SHA-256 source hashes
- matched-pair comparative calibration + conservative evidence promotion
- one-button `treat-local` transaction with ranking, preview, social-copy fallback, and experiment registration
- Python 3.11/3.12 CI

## Core rules

1. Authenticity beats generic influencer editing.
2. Retention per edit beats maximum editing.
3. A loop must earn its place.
4. Reordering must remain materially truthful.
5. First and last seconds are both retention surfaces.
6. Mechanical or creative QC failures cannot be overruled by a flashy score.
7. Rachel-specific repeated evidence outranks generic social-media folklore.
8. One viral video is a hypothesis, not a permanent rule.
9. AI may choose timestamps; deterministic code should execute them.
10. Performance belongs to the exact creative fingerprint that was posted.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### Hunt loop opportunities

```bash
rle hunt-seams raw.mp4 --top 5 --match-pairs --preview-dir previews
```

### One-button treatment

```bash
rle treat-local job.json raw.mp4 \
  --output-dir rle-output \
  --head-trim 0.4 \
  --payoff 4.1:4.8 \
  --alternate-hook 1.2:1.8 \
  --text "watch her eyes" \
  --content-class baby_reaction \
  --hook-type curiosity \
  --motion-level medium
```

### Record screenshot-derived analytics

```bash
rle record-screenshot-metrics job.json analytics.png \
  --platform youtube_shorts \
  --variant loop \
  --views 1200 \
  --apv 215% \
  --average-watch 12.6 \
  --confidence .99
```

### Compare a pattern

```bash
rle compare-pattern comparable-posts.json \
  --field loop_type \
  --treatment visual_loop \
  --control none
```

## Important docs

- `LOOP_PLAYBOOK.md` — loop selection and Seam Hunter rules
- `QUALITY_CONTROL.md` — creative QC
- `docs/V0_9_LOOP_INTELLIGENCE.md` — v0.9 architecture
- `docs/ZERO_CREDIT_RENDERING.md` — deterministic execution philosophy
- `analytics/metrics-schema.md` — performance/fingerprint/provenance schema
- `docs/MILESTONES.md` — implementation gates

## Current highest-ROI gate

The software machinery is no longer the main bottleneck. Feed real Rachel posts through v0.9, capture early/24h/72h analytics snapshots, and accumulate enough matched evidence to learn which loop types, runtimes, hooks, and text treatments repeatedly create extreme replay behavior.
