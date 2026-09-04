# Rachel Loop Engine

A retention-first short-form video editing system for turning Rachel's raw vertical footage into polished, natural, replay-friendly social videos.

## Mission

Reduce the operating workflow to:

`raw video -> analysis -> edit plan -> polished variants -> loop QC -> export -> performance feedback -> better future edits`

The system should preserve Rachel's authentic voice and family moments while making every edit earn its place through retention, clarity, emotion, or replay value.

## Core principles

1. **Authenticity beats generic influencer editing.**
2. **Retention per edit beats maximum editing.**
3. **A loop is used only when it improves the video.**
4. **The strongest moment may become the opening, even if it happened later in the raw clip.**
5. **The final second is treated as seriously as the first second.**
6. **Every published video is an experiment that teaches the system.**
7. **Rachel-specific evidence outranks generic social-media advice.**
8. **Do not optimize a metric by making the content feel fake, confusing, or manipulative.**

## Default output

- Vertical 9:16
- 1080x1920
- 30 fps unless source/platform requires otherwise
- Captions enabled by default
- Clean, natural audio
- No forced CTA when it harms the loop
- Three variants when the raw footage supports meaningful alternatives:
  - **A — Natural:** safest, most authentic edit
  - **B — Retention:** tighter and more aggressive
  - **C — Loop:** strongest viable replay/loop construction

## Repository map

- `AGENTS.md` — rules for AI agents working in this repo
- `WORKFLOW.md` — end-to-end operating procedure
- `RACHEL_STYLE.md` — Rachel-specific editing voice and guardrails
- `RETENTION_RULES.md` — pacing and retention heuristics
- `LOOP_PLAYBOOK.md` — loop strategies and selection logic
- `QUALITY_CONTROL.md` — pre-export QC gates
- `architecture/PIPELINE.md` — target technical architecture
- `prompts/` — reusable editing-agent prompts
- `config/` — machine-readable defaults
- `analytics/` — performance metrics and learned rules
- `experiments/` — test log and winning patterns
- `docs/AUTOMATION_ROADMAP.md` — path from assisted editing to one-input automation
- `src/rachel_loop_engine/` — starter automation code and data models
- `tests/` — deterministic tests

## Current milestone

**Milestone 1: Operational Editing Brain**

Create a stable, versioned set of instructions that can consistently take a raw Rachel video and produce a strong edit plan and loop-aware final cut.

## Next milestone

**Milestone 2: One-input automation**

Connect raw-video intake to transcription/analysis, editing, variant generation, QC, export, and a feedback loop using Descript and supporting services.

## Success condition

Rachel should be able to provide a raw video and have the system make most editing decisions automatically while preserving enough review control to prevent bad cuts, artificial loops, or loss of authenticity.
