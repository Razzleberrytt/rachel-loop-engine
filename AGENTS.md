# AGENTS.md — Rachel Loop Engine Operating Contract

This file is the entry point for any AI agent working on this repository.

## Primary objective

Improve the probability that a raw Rachel video becomes a watchable, authentic, replay-friendly short-form video with minimal manual editing work.

## Priority order

When rules conflict, optimize in this order:

1. Preserve truth/context and the subject's authentic personality.
2. Protect obvious safety/privacy boundaries, especially around children and personal information.
3. Make the opening immediately understandable or intriguing.
4. Remove material that does not earn its runtime.
5. Preserve emotional payoff and natural reactions.
6. Improve completion and replay likelihood.
7. Improve visual/audio polish.
8. Add stylistic effects only when they serve one of the priorities above.

## Hard rules

- Never force a loop that creates a factual or conversationally misleading meaning.
- Never fabricate speech, reactions, events, or context.
- Never cut a child's words/actions into a meaning the source footage does not support.
- Do not add a generic CTA by default.
- Do not assume loud captions, constant zooms, or meme effects improve retention.
- Do not overwrite evidence-based Rachel-specific rules with generic creator advice.
- Keep source footage outside Git history; store only metadata, plans, proxies if appropriate, and links/IDs.

## Standard agent output for a raw clip

Produce a structured decision package containing:

- one-sentence premise
- strongest 1–3 hook candidates with timestamps
- dead-air/removal candidates
- must-keep moments
- story/order recommendation
- loop candidates and loop score
- caption treatment
- audio treatment
- visual punch-in/reframe notes
- A/B/C variant plan
- risks or reasons not to loop
- final QC checklist result

## Learning rule

If analytics contradict a heuristic, record the result in `experiments/experiment-log.md`. Promote only repeatable winners to `experiments/winners.md` and then into the canonical rules.

## Definition of done

An edit is not done merely because it exports. It is done when:

- the first second has a purpose;
- there is no obvious removable dead section;
- the payoff remains emotionally intact;
- captions are legible and accurate;
- the ending has been deliberately designed;
- the restart has been checked if a loop is used;
- the edit passes `QUALITY_CONTROL.md`.
