# Milestones

## M1 — Operational Editing Brain ✅
Versioned Rachel-specific creative rules, retention rules, loop playbook, prompts, and QC principles.

## M2 — Executable Orchestration ✅
Durable jobs/manifests, validation, transport boundary, Descript coordinator, mock transport, CLI, CI, retries/idempotency.

## M2.5 — Live media bridge ✅
Synthetic URL import was verified first. The first real calibration then verified ChatGPT attachment → staging/connector transport → Descript import → `00 Raw`. Public Git transport is not required and must not be used for family footage.

## M3 — Automatic Multi-variant Production ✅ / 🟡 calibration continues
The first real clip produced `A Natural`, `B Retention`, and `C Loop` in Descript. The agent then hit an AI-credit ceiling, proving that mechanical execution must not depend on editor-agent credits.

## M3.5 — One-input Full Treatment ✅
The orchestration contract sequences source → variants → QC → render → recommendation and preserves hard failure gates.

## M3.75 — Zero-credit deterministic renderer ✅
Version 0.7 adds portable EDLs, deterministic retained-range planning, source-contiguous cyclic loop rotation, FFmpeg execution, and CLI commands for planning/rendering without Descript AI-agent credits. Descript is optional rather than canonical.

## M4 — Analytics Learning Loop 🟡 foundation
Metrics normalization, relative lift, and conservative evidence promotion exist; real post data is still needed.

## M5 — One-button intake 🟡
Direct chat attachment intake has been proven. Remaining work is packaging intake → analysis → plan → local A/B/C → QC → returned outputs behind one command/UI action with cleanup and durable job state.
