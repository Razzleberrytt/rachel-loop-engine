from types import SimpleNamespace

from rachel_loop_engine.adapters.ffmpeg import FfmpegAdapter
from rachel_loop_engine.edl import LocalEditPlan, Segment
from rachel_loop_engine.media import MediaInfo, MediaProbe
from rachel_loop_engine.render_qc import RenderInspector
from rachel_loop_engine.seam_hunter import SeamHunter


def test_media_probe_detects_silent_video():
    payload = '{"streams":[{"codec_type":"video","codec_name":"h264","width":1080,"height":1920,"avg_frame_rate":"30/1"}],"format":{"duration":"5.87"}}'
    def runner(cmd, **kwargs):
        return SimpleNamespace(stdout=payload)
    info = MediaProbe(runner=runner).probe("silent.mp4")
    assert info.has_video and not info.has_audio
    assert info.fps == 30.0
    assert info.duration_seconds == 5.87


def test_ffmpeg_video_only_command_never_references_audio_stream():
    plan = LocalEditPlan("loop", [Segment(1, 3), Segment(0, 1)], "loop.mp4", loop_anchor=1)
    cmd = FfmpegAdapter().build_command("raw.mp4", "out.mp4", plan, has_audio=False)
    graph = cmd[cmd.index("-filter_complex") + 1]
    assert "[0:a]" not in graph
    assert "a=0" in graph
    assert "-an" in cmd


class _Frames:
    def sample(self, source_path, at_seconds):
        # Smooth around 1.0s, intentionally ugly around 2.0s.
        if abs(at_seconds - 1.0) < 0.08:
            value = 100
        elif abs(at_seconds - 1.2) < 0.08:
            value = 125
        elif abs(at_seconds - 2.0) < 0.08:
            value = 240 if at_seconds > 2 else 5
        else:
            value = int((at_seconds * 17) % 255)
        return bytes([value]) * 64


class _Audio:
    def rms(self, source_path, start_seconds, duration_seconds):
        return 100.0


def test_seam_hunter_ranks_smoother_anchor_higher():
    hunter = SeamHunter(frame_sampler=_Frames(), audio_sampler=_Audio())
    candidates = hunter.hunt(
        "x.mp4",
        duration_seconds=3.0,
        fps=30,
        has_audio=True,
        step_seconds=1.0,
        start_margin=1.0,
        end_margin=1.0,
        top_n=2,
        min_spacing_seconds=0.1,
    )
    assert candidates
    assert candidates[0].anchor_seconds == 1.0
    assert candidates[0].score > 50


class _Probe:
    def probe(self, path):
        return MediaInfo(str(path), 5.0, True, False, 1080, 1920, 30.0, "h264", None)


def test_render_inspector_checks_decode_and_expected_shape():
    calls = []
    def runner(cmd, **kwargs):
        calls.append(cmd)
        if "blackdetect" in " ".join(cmd):
            return SimpleNamespace(returncode=0, stderr="")
        return SimpleNamespace(returncode=0, stderr="")
    inspection = RenderInspector(probe=_Probe(), runner=runner).inspect(
        "out.mp4",
        expected_duration=5.0,
        expected_width=1080,
        expected_height=1920,
        expected_fps=30,
        expected_audio=False,
    )
    assert inspection.passed
    assert inspection.decode_ok
    assert calls
