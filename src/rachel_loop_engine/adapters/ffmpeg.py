from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable

from ..edl import LocalEditPlan, TextOverlay
from ..media import MediaProbe


@dataclass(frozen=True)
class LocalRenderRef:
    path: str
    variant: str
    expected_duration: float
    loop_seam_source_contiguous: bool
    has_audio: bool | None = None


class FfmpegAdapter:
    """Credit-free deterministic media executor."""

    def __init__(
        self,
        *,
        ffmpeg_bin: str = "ffmpeg",
        runner: Callable[..., object] = subprocess.run,
        probe: MediaProbe | None = None,
    ) -> None:
        self.ffmpeg_bin = ffmpeg_bin
        self.runner = runner
        self.probe = probe or MediaProbe()

    def build_command(
        self,
        source_path: str | Path,
        output_path: str | Path,
        plan: LocalEditPlan,
        *,
        preset: str = "veryfast",
        crf: int = 18,
        has_audio: bool = True,
    ) -> list[str]:
        filters: list[str] = []
        concat_inputs: list[str] = []

        for i, seg in enumerate(plan.segments):
            scaled_w = _even(round(plan.width * seg.zoom))
            scaled_h = _even(round(plan.height * seg.zoom))
            filters.append(
                f"[0:v]trim=start={seg.source_start:.6f}:end={seg.source_end:.6f},"
                f"setpts=PTS-STARTPTS,fps={plan.fps},"
                f"scale={scaled_w}:{scaled_h}:force_original_aspect_ratio=increase,"
                f"crop={plan.width}:{plan.height},setsar=1[v{i}]"
            )
            if has_audio:
                filters.append(
                    f"[0:a]atrim=start={seg.source_start:.6f}:end={seg.source_end:.6f},"
                    f"asetpts=PTS-STARTPTS,aresample=48000[a{i}]"
                )
                concat_inputs.append(f"[v{i}][a{i}]")
            else:
                concat_inputs.append(f"[v{i}]")

        if has_audio:
            filters.append("".join(concat_inputs) + f"concat=n={len(plan.segments)}:v=1:a=1[vcat][acat]")
            filters.append(f"[acat]loudnorm=I={plan.audio_lufs:g}:TP=-1.5:LRA=11[aout]")
        else:
            filters.append("".join(concat_inputs) + f"concat=n={len(plan.segments)}:v=1:a=0[vcat]")

        video_label = "vcat"
        for i, overlay in enumerate(plan.text_overlays):
            next_label = f"vtext{i}"
            filters.append(f"[{video_label}]{_drawtext_filter(overlay, plan.height)}[{next_label}]")
            video_label = next_label

        command = [
            self.ffmpeg_bin, "-y", "-v", "error", "-i", str(source_path),
            "-filter_complex", ";".join(filters),
            "-map", f"[{video_label}]",
        ]
        if has_audio:
            command += ["-map", "[aout]"]
        command += ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p"]
        if has_audio:
            command += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
        else:
            command += ["-an"]
        command += ["-movflags", "+faststart", str(output_path)]
        return command

    def render(
        self,
        source_path: str | Path,
        output_path: str | Path,
        plan: LocalEditPlan,
        *,
        source_duration: float,
        preset: str = "veryfast",
        crf: int = 18,
        has_audio: bool | None = None,
    ) -> LocalRenderRef:
        plan.validate(source_duration)
        source = Path(source_path)
        if has_audio is None:
            has_audio = self.probe.probe(source).has_audio if source.exists() else True
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        command = self.build_command(source, output, plan, preset=preset, crf=crf, has_audio=has_audio)
        self.runner(command, check=True)
        return LocalRenderRef(
            path=str(output), variant=plan.variant, expected_duration=plan.output_duration,
            loop_seam_source_contiguous=plan.loop_seam_is_source_contiguous(), has_audio=has_audio,
        )

    def repeat_video(
        self,
        input_path: str | Path,
        output_path: str | Path,
        *,
        cycles: int = 3,
        duration_seconds: float | None = None,
        has_audio: bool | None = None,
        preset: str = "veryfast",
        crf: int = 20,
    ) -> Path:
        if cycles < 2:
            raise ValueError("cycles must be >= 2")
        source = Path(input_path)
        if duration_seconds is None or has_audio is None:
            info = self.probe.probe(source)
            duration_seconds = info.duration_seconds if duration_seconds is None else duration_seconds
            has_audio = info.has_audio if has_audio is None else has_audio
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self.ffmpeg_bin, "-y", "-v", "error", "-stream_loop", str(cycles - 1),
            "-i", str(source), "-t", f"{duration_seconds * cycles:.6f}",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
        ]
        command += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"] if has_audio else ["-an"]
        command += ["-movflags", "+faststart", str(output)]
        self.runner(command, check=True)
        return output


def _drawtext_filter(overlay: TextOverlay, height: int) -> str:
    text = _escape_drawtext(overlay.text)
    y = round(height * overlay.y_ratio)
    return (
        f"drawtext=text='{text}':x=(w-text_w)/2:y={y}:fontsize={overlay.font_size}:"
        f"fontcolor=white:borderw={overlay.border_width}:bordercolor=black:"
        f"enable='between(t,{overlay.start_seconds:.3f},{overlay.end_seconds:.3f})'"
    )


def _escape_drawtext(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")


def _even(value: int) -> int:
    value = max(2, value)
    return value if value % 2 == 0 else value + 1
