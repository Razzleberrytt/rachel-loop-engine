# Rachel Loop Engine — Non-Mutating Composition QC

**Do not edit, trim, rename, duplicate, or otherwise mutate this composition. Inspect only.**

Review the targeted finished composition as a short-form social video. Base every score on what is actually present; do not assume missing captions, dialogue, loop behavior, or context exists.

## Review dimensions

- **story_truthfulness (0–5):** does the edit preserve the source's apparent meaning and avoid misleading chronology?
- **hook_strength (0–5):** does the first 0–2 seconds create a truthful reason to continue?
- **pacing (0–5):** is low-information time removed without flattening natural/comedic/emotional timing?
- **caption_quality (0–5 or null):** readability, timing, safe placement; null if no captions are present/needed.
- **audio_quality (0–5 or null):** dialogue clarity/naturalness; null if meaningful audio cannot be judged.
- **loop_seam (0–5 or null):** only for a genuine loop candidate. Evaluate the final ~2 seconds played directly into the first ~2 seconds. 5 = reset is exceptionally natural; null when not a loop candidate.

## Automatic fail conditions

Set `passed=false` when any of these materially apply:
- reordering changes the story's meaning;
- important context is hidden to manufacture retention;
- captions introduce a factual/name error that changes meaning;
- audio is damaged or unintelligible;
- the composition is visibly broken/cropped in a way that harms the subject;
- for a claimed loop, the loop seam is confusing or clips necessary speech/context.

## Overall score

Use 0–100 as a holistic editorial-quality score, not a platform-algorithm prediction. Authenticity and truthfulness are hard constraints; flashy editing cannot compensate for misleading meaning.

## Response contract

Return exactly the marker below followed immediately by one JSON object. No prose before it. Do not wrap the JSON in a markdown code fence.

RLE_REVIEW_JSON
{"passed":true,"overall_score":0,"story_truthfulness":0,"hook_strength":0,"pacing":0,"caption_quality":null,"audio_quality":null,"loop_seam":null,"warnings":[],"notes":[]}
