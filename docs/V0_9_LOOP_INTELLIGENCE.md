# v0.9 Loop Intelligence Suite

## Purpose

v0.9 turns Rachel Loop Engine from a deterministic editor with analytics storage into a closed-loop experimentation system.

`private source -> probe -> seam hunt -> hypothesis variants -> deterministic render -> mechanical QC -> fingerprint -> recommendation -> post -> timestamped evidence -> matched comparison -> conservative learning`

## 1. Media hardening

`MediaProbe` uses ffprobe to discover duration, dimensions, frame rate, codecs, and whether audio exists. Real renders no longer assume `[0:a]` exists. Silent phone/social exports render video-only instead of failing.

## 2. Seam Hunter

`SeamHunter.hunt()` ranks source-contiguous rotation anchors by:

- adjacent-frame visual continuity;
- opening motion usefulness;
- local audio-level continuity when audio exists.

`SeamHunter.hunt_match_pairs()` also searches non-contiguous visual-match loops. These are more experimental and require finished-media QC.

The CLI can render three-cycle previews for top rotation candidates:

```bash
rle hunt-seams raw.mp4 --top 5 --match-pairs --preview-dir previews
```

## 3. Strong mechanical QC

`RenderInspector` checks:

- full-file decode;
- duration agreement;
- 9:16 dimensions;
- frame rate;
- expected audio presence;
- black-frame duration;
- suspicious long freeze/static intervals.

Mechanical QC is a hard gate inside the one-button treatment path.

## 4. Matched comparative calibration

`experiments.py` matches treatment posts to comparable controls using platform, content class, duration, hook, caption, audio, motion, and posting-hour similarity. Loop type can then be treated as the variable instead of being accidentally baked into similarity.

Promotion still uses the existing conservative evidence gate. One viral post does not become a permanent Rachel rule.

## 5. Analytics screenshot intake

`record-screenshot-metrics` records screenshot-derived values with:

- screenshot filename;
- SHA-256 source hash;
- extraction method;
- extraction confidence;
- source capture time;
- post timestamp and derived post age.

Raw screenshots are not copied into Git by this command. The hash makes later provenance checks possible without storing private image bytes in the repository.

## 6. Creative fingerprints

Every successful local variant can receive a stable fingerprint containing:

- variant and duration;
- loop type/score;
- hook type;
- caption/text style;
- audio mode;
- cut count;
- opening timestamp;
- chronological reorder state;
- runtime reduction;
- content class;
- motion metadata.

Performance snapshots automatically use fingerprint duration rather than raw-source duration when a treatment has registered the variant.

## 7. Hypothesis-driven variants

Core A/B/C remains backward compatible. `plan-smart` and `treat-local` add variants only when inputs make them meaningful:

- compression when extra removal ranges exist;
- payoff-first when a payoff range is supplied;
- alternate-hook when an alternate source range is supplied;
- no-text control only when a real primary text overlay exists;
- visual-match loop only when Seam Hunter clears its score threshold.

Text/no-text experiments are real FFmpeg `drawtext` execution, not metadata-only duplicates.

## 8. One-button treatment

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

The run produces:

- probed media facts;
- Seam Hunter candidates;
- auditable plans;
- deterministic renders;
- mechanical QC reports;
- creative fingerprints;
- ranked variants;
- a 3-cycle preview when a loop wins;
- deterministic title/hashtags fallback;
- experiment registration marked `performance_pending`;
- a durable `treatment-report.json`.

The job manifest is updated with recommendation/fingerprints so later metrics snapshots attach to the exact creative version that was posted.
