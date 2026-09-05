# Milestones

## M1 — Operational Editing Brain ✅
Versioned Rachel-specific creative rules, retention rules, loop playbook, prompts, and QC principles.

## M2 — Executable Orchestration ✅
- durable job/source/variant/QC/artifact models
- complete JSON manifest round-tripping
- deterministic dry-run validation
- editor transport protocol
- Descript coordinator
- mock transport
- CLI
- CI tests
- retry/idempotency safeguards

## M2.5 — Live Descript Bridge ✅ URL path
Verified live with synthetic media:
- URL import
- async import wait
- project agent mutation
- canonical A/B/C creation
- project inspection / UUID resolution
- 1080p unlisted render

Direct chat-attachment byte upload remains a transport gap because this execution environment cannot perform the signed external `PUT`. Drive/Dropbox/direct-access URLs are the current private-media path.

## M3 — Automatic Multi-variant Production ✅ coordinator / 🟡 real-content validation
The coordinator creates/resolves/publishes A Natural, B Retention, and C Loop and reuses existing state on retries. The next gate is visual validation on a real Rachel clip.

## M4 — Analytics Learning Loop 🟡 foundation
Ingest retention/replay/completion metrics, compare variants, and promote repeatable wins only after an evidence gate.

## M5 — Drop-folder / one-button intake
A private raw video landing in the intake location creates a job automatically and returns finished outputs plus a concise review card.
