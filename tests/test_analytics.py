from rachel_loop_engine.analytics import VideoMetrics, relative_lift, retention_index
from rachel_loop_engine.learning import EvidenceGate, promotion_ready

def test_retention_index_and_lift():
    a = VideoMetrics(1000, 10, average_watch_seconds=8, completion_rate=.7, replay_rate=.2)
    b = VideoMetrics(1000, 10, average_watch_seconds=9, completion_rate=.8, replay_rate=.25)
    assert retention_index(b) > retention_index(a)
    assert relative_lift(b, a) > 0

def test_promotion_gate_uses_median_and_sample_count():
    gate = EvidenceGate(minimum_examples=3, minimum_relative_lift=.08)
    assert not promotion_ready([.5, .01], gate)
    assert promotion_ready([.08, .09, .20], gate)
    assert not promotion_ready([.01, .02, 1.50], gate)
