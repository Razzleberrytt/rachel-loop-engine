from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable

from ..edl import LocalEditPlan


@dataclass(frozen=True)
class LocalRenderRef:
    path: str
    variant: str
    expected_duration: float
    loop_seam_source_contiguous: bool


class FfmpegAdapter:
    """Credit-free deterministic media executor.

    It does not analyze creative intent. It executes a reviewed EDL exactly.
    Commands are passed as argv arrays, never shell strings.
    """

    def __init__(
        self,
        *,
        ffmpeg_bin: str = "ffmpeg",
        runner: Callable[..., object] = subprocess.run,
    ) -> None:
        self.ffmpeg_bin = ffmpeg_bin
        self.runner = runner

    def build_command(
        self,
        source_path: str | Path,
        output_path: str | Path,
        plan: LocalEditPlan,
        *,
        preset: str = "veryfast",
        crf: int = 18,
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
            filters.append(
                f"[0:a]atrim=start={seg.source_start:.6f}:end={seg.source_end:.6f},"
                f"asetpts=PTS-STARTPTS,aresample=48000[a{i}]"
            )
            concat_inputs.append(f"[v{i}][a{i}]")

        filters.append(
            "".join(concat_inputs)
            + f"concat=n={len(plan.segments)}:v=1:a=1[vcat][acat]"
        )
        filters.append(
            f"[acat]loudnorm=I={plan.audio_lufs:g}:TP=-1.5:LRA=11[aout]"
        )

        return [
            self.ffmpeg_bin,
            "-y", "-v", "error", "-i", str(source_path),
            "-filter_complex", ";".join(filters),
            "-map", "[vcat]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", str(output_path),
        ]

    def render(
        self,
        source_path: str | Path,
        output_path: str | Path,
        plan: LocalEditPlan,
        *,
        source_duration: float,
        preset: str = "veryfast",
        crf: int = 18,
    ) -> LocalRenderRef:
        plan.validate(source_duration)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        command = self.build_command(source_path, output, plan, preset=preset, crf=crf)
        self.runner(command, check=True)
        return LocalRenderRef(
            path=str(output),
            variant=plan.variant,
            expected_duration=plan.output_duration,
            loop_seam_source_contiguous=plan.loop_seam_is_source_contiguous(),
        )


def _even(value: int) -> int:
    value = max(2, value)
    return value if value % 2 == 0 else value + 1
