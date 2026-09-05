from rachel_loop_engine.analytics import (
    PerformanceSnapshot,
    VideoMetrics,
    append_snapshot,
    latest_snapshot,
    load_snapshots,
    relative_lift,
    retention_index,
)
from rachel_loop_engine.learning import EvidenceGate, promotion_ready


def test_retention_index_and_lift():
    a = VideoMetrics(1000, 10, average_watch_seconds=8, completion_rate=.7, replay_rate=.2)
    b = VideoMetrics(1000, 10, average_watch_seconds=9, completion_rate=.8, replay_rate=.25)
    assert retention_index(b) > retention_index(a)
    assert relative_lift(b, a) > 0


def test_average_percentage_viewed_preserves_loop_rewatch_ratio():
    m = VideoMetrics(1000, 5.8, average_percentage_viewed=2.15)
    assert m.average_watch_ratio == 2.15
    assert retention_index(m) == 2.15


def test_snapshot_append_is_durable_and_derived(tmp_path):
    path = tmp_path / "snapshots.jsonl"
    snapshot = PerformanceSnapshot(
        job_id="job-1",
        variant="C Loop",
        platform="youtube_shorts",
        captured_at="2026-09-05T10:00:00-04:00",
        metrics=VideoMetrics(2000, 5.8, average_percentage_viewed=2.0, share_rate=.01),
        shares=20,
        likes=100,
    )
    append_snapshot(path, snapshot)
    rows = load_snapshots(path)
    assert len(rows) == 1
    assert rows[0]["derived"]["average_watch_ratio"] == 2.0
    assert rows[0]["derived"]["shares_per_1000_views"] == 10.0
    assert latest_snapshot(path)["variant"] == "C Loop"


def test_promotion_gate_uses_median_and_sample_count():
    gate = EvidenceGate(minimum_examples=3, minimum_relative_lift=.08)
    assert not promotion_ready([.5, .01], gate)
    assert promotion_ready([.08, .09, .20], gate)
    assert not promotion_ready([.01, .02, 1.50], gate)
