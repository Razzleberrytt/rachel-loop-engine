from pathlib import Path

from rachel_loop_engine.adapters.ffmpeg import FfmpegAdapter
from rachel_loop_engine.edl import LocalEditPlan, Segment
from rachel_loop_engine.planner import build_zero_credit_variants, retained_segments, rotate_segments_at_anchor


def test_retained_segments_merge_and_remove():
    segs = retained_segments(40.0, [(10, 15), (14, 20)], head_trim=2.0)
    assert [(s.source_start, s.source_end) for s in segs] == [(2.0, 10.0), (20.0, 40.0)]


def test_rotation_makes_source_contiguous_replay_seam():
    segs = retained_segments(38.0, [(12.15, 19.8)], head_trim=1.7)
    rotated = rotate_segments_at_anchor(segs, 31.0)
    plan = LocalEditPlan("loop", rotated, "C.mp4", loop_anchor=31.0)
    assert plan.loop_seam_is_source_contiguous()
    assert rotated[0].source_start == 31.0
    assert rotated[-1].source_end == 31.0


def test_zero_credit_variants_are_meaningfully_distinct():
    plans = build_zero_credit_variants(
        37.966667,
        remove_ranges=[(12.15, 19.8)],
        retention_head_trim=1.7,
        loop_anchor=31.0,
    )
    assert set(plans) == {"natural", "retention", "loop"}
    assert plans["natural"].segments[0].source_start == 0.0
    assert plans["retention"].segments[0].source_start == 1.7
    assert plans["loop"].loop_seam_is_source_contiguous()


def test_ffmpeg_command_is_shell_free_and_contains_exact_edl():
    plan = LocalEditPlan(
        variant="loop",
        segments=[Segment(31.0, 37.9), Segment(1.7, 12.15), Segment(19.8, 31.0)],
        output_name="C.mp4",
        loop_anchor=31.0,
    )
    cmd = FfmpegAdapter().build_command("raw.mp4", "out.mp4", plan)
    assert isinstance(cmd, list)
    graph = cmd[cmd.index("-filter_complex") + 1]
    assert "trim=start=31.000000:end=37.900000" in graph
    assert "concat=n=3:v=1:a=1" in graph
    assert "loudnorm=I=-16" in graph
    assert cmd[-1] == "out.mp4"


def test_ffmpeg_render_runner_is_injectable(tmp_path: Path):
    calls = []
    def runner(cmd, check):
        calls.append((cmd, check))
    adapter = FfmpegAdapter(runner=runner)
    plan = LocalEditPlan("natural", [Segment(0, 2)], "A.mp4")
    ref = adapter.render("raw.mp4", tmp_path / "A.mp4", plan, source_duration=3)
    assert calls and calls[0][1] is True
    assert ref.expected_duration == 2
