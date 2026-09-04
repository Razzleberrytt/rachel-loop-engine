# Automation Roadmap

## Phase 1 — Brain (v1)

Status: repository foundation.

Deliverables:
- canonical rules
- Rachel style
- loop scoring
- QC gates
- structured prompts
- metrics schema
- experiment system

## Phase 2 — Assisted Descript workflow

Goal: raw upload + one instruction should produce a strong Descript project.

Steps:
1. import raw media
2. transcribe
3. run master analysis
4. execute structural cuts
5. caption/reframe/audio pass
6. create loop candidate
7. QC
8. publish/share review version

Human role: choose/approve final variant.

## Phase 3 — Structured planner

Implement machine-readable `VideoJob`, `Moment`, `EditPlan`, `VariantPlan`, and `QCReport` objects.

The planner should output edit decisions independently of Descript. This makes the system portable.

## Phase 4 — One-input orchestrator

Target command:

`rle process <raw-video>`

Or UI:

`Upload Raw Video -> Process -> Review A/B/C -> Export`

Add:
- job state
- retries
- failure reporting
- asset IDs
- deterministic schema validation
- provenance/source timestamps

## Phase 5 — Performance ingestion

After posting, ingest platform analytics manually or via permitted APIs/connectors.

Compare:
- loop vs non-loop
- hook families
- durations
- caption styles
- structural reorder choices

## Phase 6 — Learning engine

Do not allow unconstrained self-modification.

Use:
1. experiment observation
2. evidence threshold
3. proposed rule update
4. human/agent review
5. versioned commit

This preserves an auditable history of why the editor changes behavior.

## Phase 7 — Scale

Potential additions:
- batch processing
- auto-selection of the best raw clip from several takes
- platform-specific variants
- thumbnail/frame selection where relevant
- analytics dashboards
- automatic experiment assignment
- winner/challenger policy for editing strategies
