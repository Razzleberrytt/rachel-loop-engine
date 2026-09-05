# Loop Playbook

## Goal

Create a restart that feels natural enough that a viewer may continue watching without immediately experiencing a hard reset.

## Loop types

1. **Sentence loop** — final words feed the opening words without changing meaning.
2. **Visual match loop** — end and opening composition/motion visually match.
3. **Motion-cut loop** — cut during meaningful movement so the eye has less time to inspect continuity.
4. **Payoff-return loop** — open with a genuine payoff glimpse; ending supplies cause/context that sends the viewer back.
5. **Audio bridge loop** — ending ambience/cadence flows into opening audio.
6. **Interrupted completion loop** — opening truthfully supplies the semantic beat implied by the ending; use carefully.
7. **Cyclical action loop** — naturally repeating action, especially useful for cute/family moments.
8. **Source-contiguous rotation** — rotate the retained timeline around an original source boundary so replay reconstructs adjacent source moments.

## Loop scoring

Manual creative score (0–5 each): semantic continuity, visual continuity, audio continuity, opening strength, payoff preservation, detectability resistance.

`0.20S + 0.15V + 0.15A + 0.20H + 0.20P + 0.10D`

- 4.2–5.0 strong
- 3.6–4.19 viable with QC
- 3.0–3.59 experimental
- below 3.0 reject

## Seam Hunter (v0.9)

Automatic source-contiguous anchor ranking uses:
- adjacent-frame continuity;
- opening-motion usefulness;
- local audio-level continuity when audio exists.

The highest raw score is **not automatically valid**. The anchor must still lie in retained footage after head trims/removals. `treat-local` enforces that gate.

A secondary visual-match search compares start/end frames and local motion energy. These non-contiguous loops are experimental and require finished-render QC before posting.

## Three-cycle QC

Review at least three consecutive cycles. `rle hunt-seams --preview-dir ...` and `treat-local` can create three-cycle previews.

Check:
- spatial jump or subject teleportation;
- lighting/color reset;
- audio pop or ambience reset;
- speech cadence reset;
- text timing reset;
- payoff still satisfying;
- first-pass comprehension intact.

Mechanical QC additionally checks decode, duration, dimensions, FPS, audio-stream expectations, black frames, and long freeze/static intervals.

## Do not force a loop when

- it changes the meaning of a statement;
- it makes a child/family interaction misleading;
- the best ending is emotionally final;
- the loop requires distracting effects;
- the opening becomes weaker;
- the audience would be confused without missing context.

A high Seam Hunter score is a candidate-generation signal, never permission to violate truthfulness or story quality.
