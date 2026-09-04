# Pipeline Architecture

## Target user experience

Rachel/Willie supplies one raw video. The system returns review-ready variants with an edit report.

## Logical pipeline

1. **Ingest** — receive file or cloud URL; store asset metadata.
2. **Transcribe** — word timestamps + speaker segments where useful.
3. **Visual analysis** — scene/motion/reaction/action timeline.
4. **Moment map** — label hook/context/payoff/dead-air/loop-bridge regions.
5. **Planner** — choose structure and generate A/B/C edit decision lists (EDLs).
6. **Editor adapter** — execute EDL in Descript or another NLE service.
7. **Caption pass** — style and correct captions.
8. **Audio pass** — dialogue level, noise cleanup, transition smoothing.
9. **Loop pass** — engineer and verify seam for candidate C.
10. **QC agent** — compare finished edit against rules and source intent.
11. **Export** — create platform-ready files.
12. **Analytics ingest** — capture post-performance metrics.
13. **Learning layer** — compare experiments and promote repeatable rules.

## System boundaries

### GitHub repo
Stores:
- rules
- prompts
- code
- configs
- schemas
- experiment results
- anonymized metadata

Does not store:
- full raw videos
- finished full-resolution videos
- secrets/API keys

### Media storage
Use Google Drive, Dropbox, object storage, or the editor's project storage for video assets.

### Descript
Initial execution engine for:
- transcription
- timeline editing
- captions
- reframing
- audio cleanup
- exports

Keep Descript behind an adapter so the planner is not permanently coupled to one editor.

## Core intermediate representation

Each variant should eventually compile into an Edit Decision List (EDL)-like JSON object:

```json
{
  "variant": "C",
  "segments": [
    {"source_start": 12.2, "source_end": 14.8, "role": "hook"},
    {"source_start": 2.1, "source_end": 9.7, "role": "context"}
  ],
  "captions": {"mode": "phrase"},
  "loop": {"enabled": true, "type": "payoff_return"}
}
```

This makes the creative plan portable across editing tools.

## Reliability strategy

- Every stage emits structured output.
- Creative agents propose decisions; deterministic validators check schemas and hard rules.
- Keep source timestamps for traceability.
- Failed automation should degrade to a reviewable edit plan rather than silently exporting junk.
