from pathlib import Path

from rachel_loop_engine.analytics import VideoMetrics, screenshot_provenance
from rachel_loop_engine.edl import LocalEditPlan, Segment
from rachel_loop_engine.experiments import ComparablePost, compare_pattern
from rachel_loop_engine.fingerprint import fingerprint_from_plan
from rachel_loop_engine.learning import EvidenceGate


def test_creative_fingerprint_is_stable_and_sensitive():
    plan = LocalEditPlan(
        "loop",
        [Segment(3, 6), Segment(0, 3)],
        "C.mp4",
        loop_anchor=3,
        metadata={"hook_type": "curiosity", "content_class": "baby_reaction", "caption_style": "single_phrase"},
    )
    a = fingerprint_from_plan(plan, source_duration=6, loop_score=91)
    b = fingerprint_from_plan(plan, source_duration=6, loop_score=91)
    c = fingerprint_from_plan(plan, source_duration=6, loop_score=70)
    assert a.fingerprint_id == b.fingerprint_id
    assert a.fingerprint_id != c.fingerprint_id
    assert a.chronological_reorder


def test_screenshot_provenance_hashes_source_without_storing_full_path(tmp_path: Path):
    shot = tmp_path / "analytics.png"
    shot.write_bytes(b"fake-image-bytes")
    provenance = screenshot_provenance(shot, extraction_method="chatgpt_vision", extraction_confidence=.98)
    assert provenance.source_kind == "analytics_screenshot"
    assert provenance.source_name == "analytics.png"
    assert len(provenance.source_sha256 or "") == 64
    assert str(tmp_path) not in (provenance.source_name or "")


def _post(post_id: str, loop_type: str, apv: float) -> ComparablePost:
    return ComparablePost(
        post_id=post_id,
        platform="youtube_shorts",
        content_class="baby_reaction",
        duration_seconds=6.0,
        hook_type="curiosity",
        loop_type=loop_type,
        caption_style="single_phrase",
        audio_mode="silent",
        motion_level="medium",
        posted_hour=20,
        metrics=VideoMetrics(1000, 6, average_percentage_viewed=apv, completion_rate=min(apv, 1.0)),
    )


def test_matched_comparison_requires_repeated_lift():
    posts = [
        _post("l1", "visual_loop", 2.0), _post("c1", "none", 1.2),
        _post("l2", "visual_loop", 1.9), _post("c2", "none", 1.1),
        _post("l3", "visual_loop", 2.1), _post("c3", "none", 1.15),
    ]
    pairs, summary = compare_pattern(
        posts,
        field="loop_type",
        treatment_value="visual_loop",
        control_value="none",
        minimum_similarity=.8,
        gate=EvidenceGate(minimum_examples=3, minimum_relative_lift=.08),
    )
    assert len(pairs) == 3
    assert summary.median_relative_lift and summary.median_relative_lift > .08
    assert summary.promotion_ready
