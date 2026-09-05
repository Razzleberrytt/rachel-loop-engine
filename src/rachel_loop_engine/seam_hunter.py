from __future__ import annotations

from array import array
from dataclasses import asdict, dataclass
from pathlib import Path
import math
import subprocess
import sys
from typing import Callable, Protocol

from .media import MediaProbe


class FrameSampler(Protocol):
    def sample(self, source_path: str | Path, at_seconds: float) -> bytes: ...


class AudioSampler(Protocol):
    def rms(self, source_path: str | Path, start_seconds: float, duration_seconds: float) -> float: ...


@dataclass(frozen=True)
class SeamCandidate:
    anchor_seconds: float
    score: float
    visual_continuity: float
    opening_motion: float
    audio_continuity: float | None
    strategy: str = "source_contiguous_rotation"

    def to_record(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MatchSeamCandidate:
    start_seconds: float
    end_seconds: float
    score: float
    frame_similarity: float
    motion_similarity: float
    opening_motion: float
    strategy: str = "visual_match_pair"

    @property
    def duration_seconds(self) -> float:
        return self.end_seconds - self.start_seconds

    def to_record(self) -> dict[str, object]:
        data = asdict(self)
        data["duration_seconds"] = self.duration_seconds
        return data


class FfmpegFrameSampler:
    """Extract tiny grayscale frames through FFmpeg; no OpenCV dependency."""

    def __init__(
        self,
        *,
        ffmpeg_bin: str = "ffmpeg",
        width: int = 64,
        height: int = 64,
        runner: Callable[..., object] = subprocess.run,
    ) -> None:
        self.ffmpeg_bin = ffmpeg_bin
        self.width = width
        self.height = height
        self.runner = runner

    def sample(self, source_path: str | Path, at_seconds: float) -> bytes:
        command = [
            self.ffmpeg_bin,
            "-v", "error",
            "-ss", f"{max(0.0, at_seconds):.6f}",
            "-i", str(source_path),
            "-frames:v", "1",
            "-vf", f"scale={self.width}:{self.height},format=gray",
            "-f", "rawvideo", "pipe:1",
        ]
        result = self.runner(command, check=True, capture_output=True)
        pixels = bytes(getattr(result, "stdout", b""))
        expected = self.width * self.height
        if len(pixels) < expected:
            raise RuntimeError(f"frame sample too short at {at_seconds:.3f}s")
        return pixels[:expected]


class FfmpegAudioSampler:
    def __init__(
        self,
        *,
        ffmpeg_bin: str = "ffmpeg",
        sample_rate: int = 8000,
        runner: Callable[..., object] = subprocess.run,
    ) -> None:
        self.ffmpeg_bin = ffmpeg_bin
        self.sample_rate = sample_rate
        self.runner = runner

    def rms(self, source_path: str | Path, start_seconds: float, duration_seconds: float) -> float:
        command = [
            self.ffmpeg_bin,
            "-v", "error",
            "-ss", f"{max(0.0, start_seconds):.6f}",
            "-t", f"{max(0.01, duration_seconds):.6f}",
            "-i", str(source_path),
            "-vn", "-ac", "1", "-ar", str(self.sample_rate),
            "-f", "s16le", "pipe:1",
        ]
        result = self.runner(command, check=True, capture_output=True)
        raw = bytes(getattr(result, "stdout", b""))
        if len(raw) < 2:
            return 0.0
        if len(raw) % 2:
            raw = raw[:-1]
        samples = array("h")
        samples.frombytes(raw)
        if sys.byteorder != "little":
            samples.byteswap()
        if not samples:
            return 0.0
        return math.sqrt(sum(float(v) * float(v) for v in samples) / len(samples))


class SeamHunter:
    """Search for replay boundaries that are visually quiet but open with energy.

    Rotation candidates are source-contiguous by construction: the output starts
    at the candidate anchor and its final segment ends at the same original source
    boundary. The scorer chooses *which* safe boundary is least noticeable and
    most useful as an opening. A secondary match-pair search can discover classic
    non-contiguous visual-match loops; those remain experimental until QC passes.
    """

    def __init__(
        self,
        *,
        probe: MediaProbe | None = None,
        frame_sampler: FrameSampler | None = None,
        audio_sampler: AudioSampler | None = None,
    ) -> None:
        self.probe = probe or MediaProbe()
        self.frames = frame_sampler or FfmpegFrameSampler()
        self.audio = audio_sampler or FfmpegAudioSampler()

    def hunt(
        self,
        source_path: str | Path,
        *,
        duration_seconds: float | None = None,
        fps: float | None = None,
        has_audio: bool | None = None,
        step_seconds: float = 0.25,
        top_n: int = 5,
        min_spacing_seconds: float = 0.50,
        start_margin: float = 0.35,
        end_margin: float = 0.35,
    ) -> list[SeamCandidate]:
        if step_seconds <= 0:
            raise ValueError("step_seconds must be > 0")
        if duration_seconds is None or fps is None or has_audio is None:
            info = self.probe.probe(source_path)
            duration_seconds = duration_seconds or info.duration_seconds
            fps = fps or info.fps or 30.0
            if has_audio is None:
                has_audio = info.has_audio
        if duration_seconds <= start_margin + end_margin:
            return []

        frame_dt = max(1.0 / max(fps, 1.0), 0.02)
        candidates: list[SeamCandidate] = []
        anchor = start_margin
        while anchor <= duration_seconds - end_margin + 1e-9:
            pre = self.frames.sample(source_path, max(0.0, anchor - frame_dt))
            post = self.frames.sample(source_path, min(duration_seconds, anchor + frame_dt))
            future = self.frames.sample(source_path, min(duration_seconds, anchor + 0.20))
            continuity = _clamp01(1.0 - _pixel_delta(pre, post))
            raw_motion = _pixel_delta(post, future)
            # Moderate opening movement masks a seam better than either a frozen
            # frame or a giant camera whip. Peak usefulness is ~12% pixel delta.
            motion_quality = _clamp01(1.0 - abs(raw_motion - 0.12) / 0.16)
            audio_continuity: float | None = None
            if has_audio:
                window = min(0.10, max(0.04, anchor / 4, (duration_seconds - anchor) / 4))
                left = self.audio.rms(source_path, max(0.0, anchor - window), window)
                right = self.audio.rms(source_path, anchor, window)
                audio_continuity = _rms_similarity(left, right)
                score = 100.0 * (0.60 * continuity + 0.22 * motion_quality + 0.18 * audio_continuity)
            else:
                score = 100.0 * (0.73 * continuity + 0.27 * motion_quality)
            candidates.append(
                SeamCandidate(
                    anchor_seconds=round(anchor, 6),
                    score=round(score, 2),
                    visual_continuity=round(continuity, 4),
                    opening_motion=round(raw_motion, 4),
                    audio_continuity=None if audio_continuity is None else round(audio_continuity, 4),
                )
            )
            anchor += step_seconds
        return _spaced_top(candidates, top_n=top_n, min_spacing=min_spacing_seconds)

    def hunt_match_pairs(
        self,
        source_path: str | Path,
        *,
        duration_seconds: float | None = None,
        step_seconds: float = 0.50,
        min_loop_seconds: float = 2.0,
        max_loop_seconds: float | None = None,
        top_n: int = 5,
    ) -> list[MatchSeamCandidate]:
        if duration_seconds is None:
            duration_seconds = self.probe.probe(source_path).duration_seconds
        if max_loop_seconds is None:
            max_loop_seconds = duration_seconds
        times: list[float] = []
        t = 0.0
        while t <= duration_seconds + 1e-9:
            times.append(round(min(t, duration_seconds), 6))
            t += step_seconds
        if times[-1] < duration_seconds:
            times.append(duration_seconds)
        samples = {time: self.frames.sample(source_path, time) for time in times}
        candidates: list[MatchSeamCandidate] = []
        for i, start in enumerate(times[:-1]):
            start_next = times[min(i + 1, len(times) - 1)]
            start_motion = _pixel_delta(samples[start], samples[start_next])
            for j in range(i + 1, len(times)):
                end = times[j]
                duration = end - start
                if duration < min_loop_seconds or duration > max_loop_seconds:
                    continue
                end_prev = times[max(i, j - 1)]
                end_motion = _pixel_delta(samples[end_prev], samples[end])
                frame_similarity = _clamp01(1.0 - _pixel_delta(samples[end], samples[start]))
                motion_similarity = _clamp01(1.0 - abs(start_motion - end_motion) / 0.35)
                opening_quality = _clamp01(1.0 - abs(start_motion - 0.12) / 0.18)
                score = 100.0 * (
                    0.72 * frame_similarity
                    + 0.18 * motion_similarity
                    + 0.10 * opening_quality
                )
                candidates.append(
                    MatchSeamCandidate(
                        start_seconds=start,
                        end_seconds=end,
                        score=round(score, 2),
                        frame_similarity=round(frame_similarity, 4),
                        motion_similarity=round(motion_similarity, 4),
                        opening_motion=round(start_motion, 4),
                    )
                )
        return sorted(candidates, key=lambda item: item.score, reverse=True)[:top_n]


def _pixel_delta(a: bytes, b: bytes) -> float:
    size = min(len(a), len(b))
    if size <= 0:
        return 1.0
    return sum(abs(a[i] - b[i]) for i in range(size)) / (255.0 * size)


def _rms_similarity(a: float, b: float) -> float:
    peak = max(abs(a), abs(b), 1.0)
    return _clamp01(1.0 - abs(a - b) / peak)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _spaced_top(
    candidates: list[SeamCandidate],
    *,
    top_n: int,
    min_spacing: float,
) -> list[SeamCandidate]:
    chosen: list[SeamCandidate] = []
    for candidate in sorted(candidates, key=lambda item: item.score, reverse=True):
        if all(abs(candidate.anchor_seconds - prior.anchor_seconds) >= min_spacing for prior in chosen):
            chosen.append(candidate)
            if len(chosen) >= top_n:
                break
    return chosen
