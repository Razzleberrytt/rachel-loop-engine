from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import json
import subprocess
from typing import Callable


@dataclass(frozen=True)
class MediaInfo:
    path: str
    duration_seconds: float
    has_video: bool
    has_audio: bool
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    audio_channels: int | None = None
    sample_rate: int | None = None


class MediaProbeError(RuntimeError):
    pass


class MediaProbe:
    """Small ffprobe wrapper used by render, seam, and QC paths.

    Keeping probing in one place prevents the renderer from assuming that every
    family clip has an audio stream (many phone/social exports do not).
    """

    def __init__(
        self,
        *,
        ffprobe_bin: str = "ffprobe",
        runner: Callable[..., object] = subprocess.run,
    ) -> None:
        self.ffprobe_bin = ffprobe_bin
        self.runner = runner

    def command(self, path: str | Path) -> list[str]:
        return [
            self.ffprobe_bin,
            "-v", "error",
            "-show_streams",
            "-show_format",
            "-of", "json",
            str(path),
        ]

    def probe(self, path: str | Path) -> MediaInfo:
        try:
            result = self.runner(
                self.command(path),
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(str(getattr(result, "stdout", "")))
        except Exception as exc:
            raise MediaProbeError(f"unable to probe media: {path}") from exc

        streams = payload.get("streams") or []
        video = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
        duration = _number((payload.get("format") or {}).get("duration"))
        if duration is None:
            candidates = [_number(s.get("duration")) for s in streams]
            duration = max((v for v in candidates if v is not None), default=None)
        if duration is None or duration <= 0:
            raise MediaProbeError(f"media duration is unavailable or invalid: {path}")

        return MediaInfo(
            path=str(path),
            duration_seconds=duration,
            has_video=video is not None,
            has_audio=audio is not None,
            width=_integer(video.get("width")) if video else None,
            height=_integer(video.get("height")) if video else None,
            fps=_rate(video.get("avg_frame_rate") or video.get("r_frame_rate")) if video else None,
            video_codec=str(video.get("codec_name")) if video and video.get("codec_name") else None,
            audio_codec=str(audio.get("codec_name")) if audio and audio.get("codec_name") else None,
            audio_channels=_integer(audio.get("channels")) if audio else None,
            sample_rate=_integer(audio.get("sample_rate")) if audio else None,
        )


def _number(value: object) -> float | None:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number


def _integer(value: object) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _rate(value: object) -> float | None:
    if value in (None, "", "0/0"):
        return None
    try:
        if isinstance(value, str) and "/" in value:
            return float(Fraction(value))
        return float(value)  # type: ignore[arg-type]
    except (ValueError, ZeroDivisionError, TypeError):
        return None
