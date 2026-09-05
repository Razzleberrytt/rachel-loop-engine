# Automation Roadmap

## Target experience

Rachel records a normal phone video. The operator supplies the raw file once. The system returns polished, captioned, loop-aware variants plus a concise review summary.

## Completed foundation

- versioned creative brain and Rachel-specific guardrails
- loop scoring and deterministic plan QC
- durable job/source/artifact manifests
- CLI and dry-run validation
- transport-neutral editor boundary
- Descript import/edit/inspect/publish coordinator
- named A/B/C composition workflow
- mock transport and automated tests
- analytics ranking and conservative rule-promotion foundation

## Next: live bridge

Map the in-product connected Descript tools to `EditorTransport` and persist connector job IDs. Process a real raw clip end-to-end without changing the creative rules.

## Then: automated analysis

Add a video-capable analyzer that outputs structured moments (hook/context/payoff/reaction/dead-air/loop-bridge/risk), transcript, premise, and candidate loop scores. Require schema validation before edits are issued.

## Then: review minimization

Generate a compact review card containing:
- A/B/C duration
- chosen hook
- loop type/viability
- major reorderings
- QC warnings
- recommended publish variant

Human review becomes exception-based rather than frame-by-frame.

## Then: feedback learning

Ingest platform metrics, compare comparable variants, and promote patterns only after the evidence gate is satisfied. One viral outlier must never rewrite permanent style rules.

## Ultimate state

`raw upload -> automated job -> A/B/C edits -> QC -> approved exports -> metrics ingest -> evidence-backed learning`
