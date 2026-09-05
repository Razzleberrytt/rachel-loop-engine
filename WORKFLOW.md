# Rachel Loop Engine — End-to-End Workflow

## 0. Intake

Receive one raw source. Create a stable job ID and record URI/upload identity, duration, filename, language, and premise if known. Never store raw media in Git.

## 1. Understand the whole source

Transcribe and inspect the entire clip before editing. Mark candidate moments as hook, context, payoff, reaction, support, dead-air, duplicate, loop-bridge, or risk. Preserve ambiguity rather than inventing a story.

## 2. Build three intents

### A Natural
Clean, clear, authentic. Minimal reorder. Remove recording artifacts and low-value pauses.

### B Retention
Use the strongest truthful opening, denser pacing, and more structural compression. Reordering must remain materially truthful.

### C Loop
Start from the strongest story structure and attempt a natural reset using movement, sentence, audio, payoff-to-premise, or visual bridging. Reject the loop if the seam or meaning is bad.

## 3. Execute in editor

For Descript, create `00 Raw`, preserve it, then create canonical A/B/C compositions. Use versioned prompts from the repo. Inspect the project after agent work and resolve real composition IDs by canonical name.

## 4. Polish

- vertical safe framing
- natural dialogue cleanup
- readable phrase-based captions
- restrained punch-ins/reframes
- no generic CTA that weakens the ending
- no unnecessary outro tail/fade/dead air

## 5. QC

Run deterministic plan checks and media-aware checks. For loop variants, replay final 2 seconds into first 2 seconds. A rejected loop does not block Natural/Retention.

## 6. Publish/export

Publish only accepted compositions. Default target is 1080p, unlisted review output until posting is intentional. Persist project ID, composition IDs, output/share refs, durations, and QC state.

## 7. Observe

Record platform metrics that actually exist. Do not infer replay/completion fields the platform did not provide.

## 8. Learn

Compare comparable posts/variants. Promote a pattern only after it clears the evidence gate (default: at least 3 examples and median relative lift >= 8%) and does not damage authenticity/safety.

## Recovery rule

Retry only the failed stage. Import success must survive edit failure; edit success must survive publish failure; published variants must not be duplicated because another variant failed.
