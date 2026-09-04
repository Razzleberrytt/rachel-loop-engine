# End-to-End Workflow

## Stage 0 — Intake

Input: one raw video, ideally the original phone file.

Capture:
- source filename / asset ID
- source duration
- orientation and resolution
- platform target(s)
- optional creator note
- whether children/minors appear

Do not require Rachel to pre-trim the clip.

## Stage 1 — Understand before cutting

Transcribe the full clip and inspect visual events. Determine:
- What is actually happening?
- What is the emotional reason to watch?
- Where is the strongest moment?
- Is there a story, reaction, reveal, cute moment, joke, problem/solution, or transformation?
- Does the raw recording already contain a natural loop opportunity?

Output a one-sentence premise.

## Stage 2 — Build a moment map

Mark timestamp ranges as one of:
- HOOK
- CONTEXT
- PAYOFF
- REACTION
- SUPPORT
- DEAD_AIR
- DUPLICATE
- LOOP_BRIDGE
- RISK

The moment map is the basis for all later decisions.

## Stage 3 — Hook selection

Generate up to three hook candidates. Score each on:
- immediate clarity
- curiosity
- emotional intensity
- visual activity
- connection to the payoff
- authenticity

Prefer an authentic high-value moment from later in the footage over a weak chronological opening.

## Stage 4 — Structural edit

Choose the minimum runtime necessary to preserve the experience.

Typical structures:

### Natural story
`hook -> context -> development -> payoff -> clean ending`

### Payoff-first
`payoff glimpse -> context -> development -> payoff continuation -> loop/ending`

### Reaction-led
`reaction -> cause -> escalation -> return to reaction`

### Seamless-loop story
`opening phrase/action -> body -> bridge that naturally feeds opening`

Do not use a structure simply because it is trendy.

## Stage 5 — Tightening

Remove or shorten:
- dead air
- accidental setup
- repeated explanations
- filler phrases that add no personality
- long camera settling periods
- empty tails after the payoff

Preserve:
- natural comedic timing
- emotionally meaningful pauses
- genuine reactions
- context required to understand the moment

## Stage 6 — Visual treatment

Default visual treatment is restrained.

Use punch-ins when they:
- emphasize a reaction;
- hide a jump cut;
- redirect attention;
- create controlled visual change during a long static beat.

Avoid constant zooming.

Reframe to keep the important subject/action visible in 9:16. Never crop out meaningful context for the sake of face centering.

## Stage 7 — Captions

Generate accurate captions and correct obvious transcription errors.

Default:
- phrase-based rather than giant word-by-word captions
- high contrast
- safe margins for platform UI
- emphasis only on genuinely important words
- avoid covering faces, hands, or the key action

## Stage 8 — Audio

- normalize dialogue
- reduce distracting background noise conservatively
- preserve natural room tone
- avoid robotic over-processing
- use music only when it helps; speech clarity wins
- ensure the loop transition does not produce an audible click or ambience jump

## Stage 9 — Loop engineering

Evaluate loop options using `LOOP_PLAYBOOK.md`.

A loop must pass:
- semantic continuity
- visual continuity
- audio continuity
- no obvious end-card cadence
- no loss of payoff

If no loop scores high enough, export a non-looping version.

## Stage 10 — Variants

When meaningful differences exist, create:

### A — Natural
Closest to authentic chronology and pacing.

### B — Retention
Tighter opening, more aggressive removal, stronger structural reorder where justified.

### C — Loop
Best loop-capable construction, even if its edit order differs from A/B.

Do not create fake variants that differ only by a tiny cosmetic change.

## Stage 11 — QC

Run every final variant through `QUALITY_CONTROL.md`.

## Stage 12 — Export

Default:
- 1080x1920
- 9:16
- 30 fps
- H.264/AAC unless platform/tool requires otherwise
- no watermark

## Stage 13 — Feedback

After posting, record:
- platform
- post date/time
- video length
- views
- average watch time
- average percentage viewed if available
- completion rate if available
- replay/loop proxy if available
- likes/comments/shares/saves
- follows attributable if available
- qualitative comments

Use performance to update experiments, not to rewrite canonical rules after one result.
