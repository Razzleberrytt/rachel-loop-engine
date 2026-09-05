# Performance Metrics Schema

Record what the platform actually exposes; do not invent missing metrics.

## Storage rule
Performance snapshots are append-only. A later screenshot or refresh creates a new snapshot rather than replacing an earlier one. The default CLI target is `analytics/performance-snapshots.jsonl`.

Percentages are stored as ratios:
- `100%` -> `1.0`
- `215%` -> `2.15`

Do **not** cap average percentage viewed or watch-time ratio at `1.0`; replay-heavy short-form loops can legitimately exceed 100%.

## Identity
- job_id
- video_id
- source_asset_id (if available)
- variant (A/B/C or exact keeper label)
- platform
- post_url or platform post ID
- post_timestamp (if known)
- captured_at
- duration_seconds

## Reach
- views
- unique_viewers (if available)
- impressions (if available)

## Watch behavior
- average_watch_time_seconds
- average_percentage_viewed
- completion_rate
- 3_second_views / equivalent
- replay_count or replay proxy if the platform exposes one

## Engagement
- likes
- comments
- shares
- saves
- follows_attributed

## Derived metrics
- watch_time_ratio = average_watch_time_seconds / duration_seconds, or average_percentage_viewed when direct watch time is unavailable
- retention_index
- engagement_per_view
- shares_per_1000_views
- comments_per_1000_views
- follows_per_1000_views

## Creative metadata
- hook_type
- loop_type
- loop_score
- opening_source_timestamp
- chronological_reorder (yes/no)
- caption_style
- estimated_cut_count
- runtime_reduction_percent

## CLI capture

```bash
rle record-metrics job.json \
  --platform youtube_shorts \
  --variant "C Loop" \
  --views 2500 \
  --apv 215% \
  --likes 100 \
  --shares 25
```

`--apv`, `--completion`, and `--replay-rate` accept either decimals (`2.15`) or percent strings (`215%`).

## Notes
Capture qualitative signals such as comments indicating viewers rewatched, did not notice the restart, were confused, or specifically reacted to the hook/payoff.
