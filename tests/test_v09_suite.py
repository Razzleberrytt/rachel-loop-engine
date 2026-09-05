from rachel_loop_engine.adapters.ffmpeg import FfmpegAdapter
from rachel_loop_engine.edl import LocalEditPlan, Segment, TextOverlay
from rachel_loop_engine.planner import build_hypothesis_variants, move_range_to_front


def test_payoff_first_reorders_without_duplicating_runtime():
    original = [Segment(0, 3), Segment(5, 8)]
    moved = move_range_to_front(original, (6, 7))
    assert moved[0].source_start == 6
    assert round(sum(s.duration for s in moved), 6) == 6.0


def test_smart_variants_only_add_hypotheses_that_have_inputs():
    basic = build_hypothesis_variants(10, retention_head_trim=1)
    assert set(basic) == {"natural", "retention"}
    rich = build_hypothesis_variants(
        10,
        retention_head_trim=1,
        loop_anchor=5,
        payoff_range=(7, 8),
        alternate_hook_range=(3, 4),
        primary_text="watch her eyes",
    )
    assert {"natural", "retention", "loop", "payoff_first", "alternate_hook", "minimal_text"} <= set(rich)
    assert rich["retention"].text_overlays
    assert not rich["minimal_text"].text_overlays


def test_drawtext_is_real_render_instruction_not_metadata_only():
    plan = LocalEditPlan(
        "retention",
        [Segment(0, 3)],
        "B.mp4",
        text_overlays=[TextOverlay("watch her eyes", 0, 2)],
    )
    cmd = FfmpegAdapter().build_command("raw.mp4", "out.mp4", plan, has_audio=False)
    graph = cmd[cmd.index("-filter_complex") + 1]
    assert "drawtext=" in graph
    assert "watch her eyes" in graph
    assert "-an" in cmd
