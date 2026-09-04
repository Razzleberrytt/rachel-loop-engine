# Performance Metrics Schema

Record what the platform actually exposes; do not invent missing metrics.

## Identity
- video_id
- source_asset_id
- variant (A/B/C)
- platform
- post_url or platform post ID
- post_timestamp
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
- watch_time_ratio = average_watch_time_seconds / duration_seconds
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

## Notes
Capture qualitative signals such as comments indicating viewers rewatched, did not notice the restart, were confused, or specifically reacted to the hook/payoff.
