from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
import subprocess
from typing import Callable

from .media import MediaInfo, MediaProbe


@dataclass(frozen=True)
class RenderInspection:
    passed: bool
    score: float
    path: str
    duration_seconds: float | None
    width: int | None
    height: int | None
    fps: float | None
    has_audio: bool | None
    decode_ok: bool
    black_seconds: float = 0.0
    frozen_seconds: float = 0.0
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_record(self) -> dict[str, object]:
        return asdict(self)


class RenderInspector:
    """Mechanical publish gate for finished files.

    This does not judge whether a joke/reaction is good. It proves boring but
    essential things: the file decodes, dimensions/fps/duration are sane, audio
    expectations are met, and obvious black/freeze artifacts are surfaced.
    """

    def __init__(
        self,
        *,
        probe: MediaProbe | None = None,
        ffmpeg_bin: str = "ffmpeg",
        runner: Callable[..., object] = subprocess.run,
    ) -> None:
        self.probe = probe or MediaProbe()
        self.ffmpeg_bin = ffmpeg_bin
        self.runner = runner

    def inspect(
        self,
        path: str | Path,
        *,
        expected_duration: float | None = None,
        expected_width: int | None = None,
        expected_height: int | None = None,
        expected_fps: float | None = None,
        expected_audio: bool | None = None,
        duration_tolerance: float = 0.18,
        scan_artifacts: bool = True,
    ) -> RenderInspection:
        failures: list[str] = []
        warnings: list[str] = []
        score = 100.0
        try:
            info = self.probe.probe(path)
        except Exception as exc:
            return RenderInspection(
                passed=False,
                score=0.0,
                path=str(path),
                duration_seconds=None,
                width=None,
                height=None,
                fps=None,
                has_audio=None,
                decode_ok=False,
                failures=[f"ffprobe failed: {exc}"],
            )

        if not info.has_video:
            failures.append("output has no video stream")
            score -= 60
        if expected_duration is not None and abs(info.duration_seconds - expected_duration) > duration_tolerance:
            failures.append(
                f"duration mismatch: {info.duration_seconds:.3f}s vs expected {expected_duration:.3f}s"
            )
            score -= 25
        if expected_width is not None and info.width != expected_width:
            failures.append(f"width mismatch: {info.width} vs expected {expected_width}")
            score -= 15
        if expected_height is not None and info.height != expected_height:
            failures.append(f"height mismatch: {info.height} vs expected {expected_height}")
            score -= 15
        if expected_fps is not None and info.fps is not None and abs(info.fps - expected_fps) > 0.10:
            failures.append(f"fps mismatch: {info.fps:.3f} vs expected {expected_fps:.3f}")
            score -= 15
        if expected_audio is True and not info.has_audio:
            failures.append("expected audio stream is missing")
            score -= 20
        elif expected_audio is False and info.has_audio:
            warnings.append("output contains audio although source/treatment expected silence")
            score -= 3

        decode_ok, decode_error = self._decode(path)
        if not decode_ok:
            failures.append(f"full decode failed: {decode_error or 'unknown FFmpeg error'}")
            score -= 40

        black_seconds = 0.0
        frozen_seconds = 0.0
        if scan_artifacts and info.has_video and decode_ok:
            black_seconds, frozen_seconds = self._artifact_scan(path)
            black_limit = max(0.35, min(1.0, info.duration_seconds * 0.12))
            if black_seconds > black_limit:
                failures.append(f"excess black-frame duration: {black_seconds:.3f}s")
                score -= 20
            elif black_seconds > 0.08:
                warnings.append(f"black frames detected: {black_seconds:.3f}s")
                score -= 4
            freeze_limit = max(1.50, info.duration_seconds * 0.55)
            if frozen_seconds > freeze_limit:
                warnings.append(f"long frozen/static interval detected: {frozen_seconds:.3f}s")
                score -= 6

        return RenderInspection(
            passed=not failures,
            score=max(0.0, round(score, 1)),
            path=str(path),
            duration_seconds=info.duration_seconds,
            width=info.width,
            height=info.height,
            fps=info.fps,
            has_audio=info.has_audio,
            decode_ok=decode_ok,
            black_seconds=round(black_seconds, 4),
            frozen_seconds=round(frozen_seconds, 4),
            failures=failures,
            warnings=warnings,
        )

    def _decode(self, path: str | Path) -> tuple[bool, str]:
        command = [self.ffmpeg_bin, "-v", "error", "-i", str(path), "-f", "null", "-"]
        result = self.runner(command, check=False, capture_output=True, text=True)
        returncode = int(getattr(result, "returncode", 0))
        stderr = str(getattr(result, "stderr", ""))
        return returncode == 0, stderr.strip()[-500:]

    def _artifact_scan(self, path: str | Path) -> tuple[float, float]:
        command = [
            self.ffmpeg_bin,
            "-hide_banner", "-nostats",
            "-i", str(path),
            "-vf", "blackdetect=d=0.08:pix_th=0.10,freezedetect=n=-50dB:d=0.35",
            "-an", "-f", "null", "-",
        ]
        result = self.runner(command, check=False, capture_output=True, text=True)
        stderr = str(getattr(result, "stderr", ""))
        black = sum(float(v) for v in re.findall(r"black_duration:([0-9.]+)", stderr))
        frozen = sum(float(v) for v in re.findall(r"freeze_duration:([0-9.]+)", stderr))
        return black, frozen
