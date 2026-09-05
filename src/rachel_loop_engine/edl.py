from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json

from .models import VariantKind


@dataclass(frozen=True)
class Segment:
    """One retained source interval in a deterministic edit decision list."""

    source_start: float
    source_end: float
    label: str = ""
    zoom: float = 1.0

    def __post_init__(self) -> None:
        if self.source_start < 0:
            raise ValueError("segment source_start must be >= 0")
        if self.source_end <= self.source_start:
            raise ValueError("segment must have source_start < source_end")
        if not 1.0 <= self.zoom <= 1.35:
            raise ValueError("segment zoom must be between 1.0 and 1.35")

    @property
    def duration(self) -> float:
        return self.source_end - self.source_start


@dataclass(frozen=True)
class TextOverlay:
    text: str
    start_seconds: float
    end_seconds: float
    y_ratio: float = 0.16
    font_size: int = 54
    border_width: int = 3

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("overlay text cannot be empty")
        if self.start_seconds < 0 or self.end_seconds <= self.start_seconds:
            raise ValueError("overlay must satisfy 0 <= start < end")
        if not 0 <= self.y_ratio <= 1:
            raise ValueError("y_ratio must be between 0 and 1")
        if self.font_size <= 0 or self.border_width < 0:
            raise ValueError("font_size must be > 0 and border_width >= 0")


@dataclass
class LocalEditPlan:
    """Portable, editor-independent instructions for one rendered variant."""

    variant: VariantKind
    segments: list[Segment]
    output_name: str
    width: int = 1080
    height: int = 1920
    fps: int = 30
    audio_lufs: float = -16.0
    loop_anchor: float | None = None
    notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    text_overlays: list[TextOverlay] = field(default_factory=list)

    def validate(self, source_duration: float) -> None:
        if source_duration <= 0:
            raise ValueError("source_duration must be > 0")
        if not self.segments:
            raise ValueError("edit plan must contain at least one segment")
        if self.width <= 0 or self.height <= 0 or self.fps <= 0:
            raise ValueError("width, height, and fps must be positive")
        for segment in self.segments:
            if segment.source_end > source_duration + 1e-6:
                raise ValueError(
                    f"segment ends after source duration: {segment.source_end} > {source_duration}"
                )
        if self.loop_anchor is not None and not 0 <= self.loop_anchor <= source_duration:
            raise ValueError("loop_anchor must lie inside source duration")
        for overlay in self.text_overlays:
            if overlay.end_seconds > self.output_duration + 1e-6:
                raise ValueError("text overlay extends beyond output duration")

    @property
    def output_duration(self) -> float:
        return sum(segment.duration for segment in self.segments)

    def loop_seam_is_source_contiguous(self, tolerance: float | None = None) -> bool:
        """True when replay reconnects two adjacent points from the original source."""
        if self.loop_anchor is None or not self.segments:
            return False
        if tolerance is None:
            tolerance = 1.0 / max(self.fps, 1) + 1e-6
        return (
            abs(self.segments[0].source_start - self.loop_anchor) <= tolerance
            and abs(self.segments[-1].source_end - self.loop_anchor) <= tolerance
        )


def dump_plan(plan: LocalEditPlan, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(plan), indent=2) + "\n", encoding="utf-8")
    return path


def load_plan(path: str | Path) -> LocalEditPlan:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data["segments"] = [Segment(**item) for item in data.get("segments", [])]
    data["text_overlays"] = [TextOverlay(**item) for item in data.get("text_overlays", [])]
    return LocalEditPlan(**data)
