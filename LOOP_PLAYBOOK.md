# Loop Playbook

## Goal

Create a restart that feels natural enough that a viewer may continue watching without immediately experiencing a hard reset.

## Loop types

### 1. Sentence loop
The final words syntactically or conceptually feed the opening words.

Best when:
- speech is the main content;
- a sentence can be split without changing meaning;
- room tone matches.

Risk: sounding grammatically manipulated.

### 2. Visual match loop
The final frame/action resembles or continues the opening frame/action.

Best when:
- there is repeated motion;
- camera angle is stable;
- a hand/body/camera movement can hide the seam.

Risk: visible position or lighting jump.

### 3. Motion-cut loop
Cut during meaningful movement so the eye has less time to inspect continuity.

Examples:
- turning the camera
- moving a hand across frame
- walking past camera
- quick head turn

Risk: audio can still reveal the seam.

### 4. Payoff-return loop
Open with a high-value moment; the end provides the cause/setup that logically sends the viewer back to the opening.

Best when the raw video has a strong reaction/reveal later than the setup.

Risk: spoiling too much in the opening.

### 5. Audio bridge loop
The ending audio cadence or ambience is designed to flow into the opening sound.

Risk: background-noise discontinuity.

### 6. Interrupted completion loop
The video ends at a point where the viewer expects one more semantic beat, and the opening supplies it.

Use carefully. It must not feel like content was dishonestly withheld.

### 7. Cyclical action loop
The subject performs an action that naturally repeats.

Best for visual/cute/family moments with little narrative dependency.

## Loop scoring

Score each candidate 0–5:

- semantic continuity (S)
- visual continuity (V)
- audio continuity (A)
- opening strength (H)
- payoff preservation (P)
- detectability resistance (D)

Weighted loop score:

`0.20S + 0.15V + 0.15A + 0.20H + 0.20P + 0.10D`

### Decision bands

- **4.2–5.0:** strong loop candidate
- **3.6–4.19:** viable with QC
- **3.0–3.59:** experimental only
- **below 3.0:** do not force the loop

## Seam QC

Review at least three consecutive cycles:

`...end -> start -> ...end -> start...`

Check:
- Does the eye detect a spatial jump?
- Does background noise pop?
- Does speech cadence reset?
- Does Rachel visibly teleport position?
- Is the payoff still satisfying?
- Does the viewer understand the content on the first pass?

## Do-not-loop conditions

Do not force a loop if:
- it changes the meaning of a statement;
- it makes a child/family interaction misleading;
- the best ending is emotionally final;
- the loop requires distracting effects;
- the opening becomes weaker;
- the audience would be confused without missing context.
