# Analytics Feedback Loop

The system should learn from Rachel's actual audience without confusing correlation with certainty.

## Store per post/variant
- platform
- post ID / URL
- variant kind
- video duration
- views
- average watch time when available
- completion rate when available
- replay rate when available
- shares / share rate
- saves / save rate
- follows attributable to the post when available
- posting date/time and major content context

## Ranking aid

`retention_index()` is deliberately labeled an internal experiment-ranking aid. Its weights are **not** claims about Facebook/TikTok/YouTube ranking algorithms.

## Promotion gate

A creative rule should not become permanent because one video exploded. Default promotion gate:
- at least 3 comparable examples;
- median relative lift >= 8%;
- no material authenticity/safety downside;
- ideally observed across more than one content premise.

Promoted findings move to `experiments/winners.md`, then into the relevant creative rules with the evidence noted.
