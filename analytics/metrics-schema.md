# Performance Metrics Schema

Record what the platform actually exposes; never invent missing metrics. Snapshots are append-only.

## Identity
- job_id
- video_id / platform post ID
- variant
- platform
- post_timestamp
- captured_at
- derived post_age_seconds
- duration_seconds (variant fingerprint duration when available)

## Reach
- views
- unique_viewers (if available)
- impressions (if available)

## Watch behavior
- average_watch_time_seconds
- average_percentage_viewed (may exceed 100%; store 215% as 2.15)
- completion_rate
- replay_rate or replay proxy if exposed

## Engagement
- likes
- comments
- shares
- saves
- follows_attributed

## Provenance
For screenshot-derived observations record:
- source_kind = analytics_screenshot
- screenshot filename only, not private full path
- SHA-256 of screenshot bytes
- extraction_method
- extraction_confidence
- source_captured_at
- optional notes

Do not place raw private analytics screenshots in the public repository merely to preserve provenance.

## Creative fingerprint
- fingerprint_id
- variant
- rendered duration
- source duration
- hook_type
- loop_type
- loop_score
- opening_source_timestamp
- chronological_reorder
- caption_style / text_overlay
- audio_mode
- cut_count
- payoff_position if known
- face_present if known
- motion_level / opening_motion if known
- runtime_reduction_percent
- content_class

## Derived metrics
- average_watch_ratio
- retention_index
- engagement_per_view
- shares_per_1000_views
- post_age_seconds

## Learning rule
Performance belongs to the exact creative fingerprint. Compare patterns across reasonably comparable posts and require repeated evidence before changing permanent Rachel rules.
