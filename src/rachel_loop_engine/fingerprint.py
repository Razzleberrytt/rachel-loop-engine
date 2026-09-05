from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from typing import Any

from .edl import LocalEditPlan


@dataclass(frozen=True)
class CreativeFingerprint:
    """Machine-readable creative identity attached to a rendered post.

    The fingerprint deliberately stores editing *mechanics* separately from
    performance. That lets the analytics layer ask which combinations repeatedly
    outperform without relying on memory or one-off viral anecdotes.
    """

    variant: str
    duration_seconds: float
    source_duration_seconds: float
    loop_type: str = "none"
    loop_score: float | None = None
    hook_type: str = "unknown"
    caption_style: str = "unknown"
    audio_mode: str = "unknown"
    cut_count: int = 0
    payoff_position: float | None = None
    face_present: bool | None = None
    motion_level: str = "unknown"
    opening_motion: bool | None = None
    opening_source_timestamp: float | None = None
    chronological_reorder: bool = False
    runtime_reduction_percent: float = 0.0
    content_class: str = "unknown"
    text_overlay: str = "unknown"
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0 or self.source_duration_seconds <= 0:
            raise ValueError("fingerprint durations must be > 0")
        if self.cut_count < 0:
            raise ValueError("cut_count must be >= 0")
        if self.loop_score is not None and not 0 <= self.loop_score <= 100:
            raise ValueError("loop_score must be between 0 and 100")
        if self.payoff_position is not None and not 0 <= self.payoff_position <= 1:
            raise ValueError("payoff_position must be between 0 and 1")

    @property
    def fingerprint_id(self) -> str:
        payload = json.dumps(self.normalized_record(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]

    def normalized_record(self) -> dict[str, object]:
        record = asdict(self)
        record["duration_seconds"] = round(self.duration_seconds, 4)
        record["source_duration_seconds"] = round(self.source_duration_seconds, 4)
        record["runtime_reduction_percent"] = round(self.runtime_reduction_percent, 4)
        if self.opening_source_timestamp is not None:
            record["opening_source_timestamp"] = round(self.opening_source_timestamp, 4)
        record["fingerprint_id"] = self.fingerprint_id if "fingerprint_id" not in record else record["fingerprint_id"]
        return record

    def to_record(self) -> dict[str, object]:
        record = asdict(self)
        record["fingerprint_id"] = self.fingerprint_id
        return record


def fingerprint_from_plan(
    plan: LocalEditPlan,
    *,
    source_duration: float,
    loop_type: str | None = None,
    loop_score: float | None = None,
    hook_type: str | None = None,
    caption_style: str | None = None,
    audio_mode: str | None = None,
    payoff_position: float | None = None,
    face_present: bool | None = None,
    motion_level: str | None = None,
    opening_motion: bool | None = None,
    content_class: str | None = None,
    text_overlay: str | None = None,
    extra: dict[str, Any] | None = None,
) -> CreativeFingerprint:
    if source_duration <= 0:
        raise ValueError("source_duration must be > 0")
    starts = [segment.source_start for segment in plan.segments]
    chronological_reorder = any(b < a for a, b in zip(starts, starts[1:]))
    metadata = plan.metadata
    inferred_loop = loop_type or str(metadata.get("loop_type") or ("source_contiguous_rotation" if plan.loop_anchor is not None else "none"))
    inferred_score = loop_score if loop_score is not None else _optional_float(metadata.get("loop_score"))
    reduction = max(0.0, 1.0 - plan.output_duration / source_duration) * 100
    return CreativeFingerprint(
        variant=str(plan.variant),
        duration_seconds=plan.output_duration,
        source_duration_seconds=source_duration,
        loop_type=inferred_loop,
        loop_score=inferred_score,
        hook_type=hook_type or str(metadata.get("hook_type") or "unknown"),
        caption_style=caption_style or str(metadata.get("caption_style") or "unknown"),
        audio_mode=audio_mode or str(metadata.get("audio_mode") or "unknown"),
        cut_count=max(0, len(plan.segments) - 1),
        payoff_position=payoff_position if payoff_position is not None else _optional_float(metadata.get("payoff_position")),
        face_present=face_present if face_present is not None else _optional_bool(metadata.get("face_present")),
        motion_level=motion_level or str(metadata.get("motion_level") or "unknown"),
        opening_motion=opening_motion if opening_motion is not None else _optional_bool(metadata.get("opening_motion")),
        opening_source_timestamp=plan.segments[0].source_start if plan.segments else None,
        chronological_reorder=chronological_reorder,
        runtime_reduction_percent=reduction,
        content_class=content_class or str(metadata.get("content_class") or "unknown"),
        text_overlay=text_overlay or str(metadata.get("text_overlay") or "unknown"),
        extra=dict(extra or metadata.get("fingerprint_extra") or {}),
    )


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_bool(value: object) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in {"true", "yes", "1"}:
            return True
        if value.lower() in {"false", "no", "0"}:
            return False
    return None
