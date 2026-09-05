from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean, median

from .analytics import VideoMetrics, relative_lift
from .learning import EvidenceGate, promotion_ready


@dataclass(frozen=True)
class ComparablePost:
    post_id: str
    platform: str
    content_class: str
    duration_seconds: float
    metrics: VideoMetrics
    hook_type: str = "unknown"
    loop_type: str = "none"
    caption_style: str = "unknown"
    audio_mode: str = "unknown"
    motion_level: str = "unknown"
    posted_hour: float | None = None

    def __post_init__(self) -> None:
        if not self.post_id.strip():
            raise ValueError("post_id is required")
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be > 0")
        if self.posted_hour is not None and not 0 <= self.posted_hour < 24:
            raise ValueError("posted_hour must be in [0, 24)")


@dataclass(frozen=True)
class MatchedPair:
    treatment_post_id: str
    control_post_id: str
    similarity: float
    relative_lift: float | None


@dataclass(frozen=True)
class ComparativeSummary:
    field: str
    treatment_value: str
    control_value: str
    pair_count: int
    evaluable_pairs: int
    median_relative_lift: float | None
    mean_relative_lift: float | None
    wins: int
    losses: int
    median_similarity: float | None
    promotion_ready: bool

    def to_record(self) -> dict[str, object]:
        return asdict(self)


def comparability_score(a: ComparablePost, b: ComparablePost) -> float:
    """Similarity score intentionally excludes loop_type as a default outcome variable."""
    score = 0.0
    score += 0.20 if a.platform.casefold() == b.platform.casefold() else 0.0
    score += 0.25 if a.content_class.casefold() == b.content_class.casefold() else 0.0
    duration_gap = abs(a.duration_seconds - b.duration_seconds) / max(a.duration_seconds, b.duration_seconds)
    score += 0.20 * max(0.0, 1.0 - duration_gap)
    score += 0.10 if a.hook_type == b.hook_type else 0.0
    score += 0.07 if a.caption_style == b.caption_style else 0.0
    score += 0.06 if a.audio_mode == b.audio_mode else 0.0
    score += 0.04 if a.motion_level == b.motion_level else 0.0
    if a.posted_hour is not None and b.posted_hour is not None:
        raw = abs(a.posted_hour - b.posted_hour)
        circular = min(raw, 24 - raw)
        score += 0.08 * max(0.0, 1.0 - circular / 12.0)
    return round(min(1.0, score), 4)


def build_matched_pairs(
    posts: list[ComparablePost],
    *,
    field: str,
    treatment_value: str,
    control_value: str,
    minimum_similarity: float = 0.62,
) -> list[MatchedPair]:
    if field not in {"loop_type", "hook_type", "caption_style", "audio_mode", "motion_level"}:
        raise ValueError(f"unsupported comparison field: {field}")
    treatment = [p for p in posts if str(getattr(p, field)) == treatment_value]
    controls = [p for p in posts if str(getattr(p, field)) == control_value]
    unused = {p.post_id: p for p in controls}
    pairs: list[MatchedPair] = []
    for candidate in treatment:
        ranked = sorted(
            ((comparability_score(candidate, control), control) for control in unused.values()),
            key=lambda item: item[0],
            reverse=True,
        )
        if not ranked or ranked[0][0] < minimum_similarity:
            continue
        similarity, baseline = ranked[0]
        lift = relative_lift(candidate.metrics, baseline.metrics)
        pairs.append(
            MatchedPair(
                treatment_post_id=candidate.post_id,
                control_post_id=baseline.post_id,
                similarity=similarity,
                relative_lift=lift,
            )
        )
        unused.pop(baseline.post_id, None)
    return pairs


def summarize_pairs(
    pairs: list[MatchedPair],
    *,
    field: str,
    treatment_value: str,
    control_value: str,
    gate: EvidenceGate | None = None,
) -> ComparativeSummary:
    lifts = [pair.relative_lift for pair in pairs if pair.relative_lift is not None]
    similarities = [pair.similarity for pair in pairs]
    gate = gate or EvidenceGate()
    return ComparativeSummary(
        field=field,
        treatment_value=treatment_value,
        control_value=control_value,
        pair_count=len(pairs),
        evaluable_pairs=len(lifts),
        median_relative_lift=round(median(lifts), 4) if lifts else None,
        mean_relative_lift=round(mean(lifts), 4) if lifts else None,
        wins=sum(1 for lift in lifts if lift > 0),
        losses=sum(1 for lift in lifts if lift < 0),
        median_similarity=round(median(similarities), 4) if similarities else None,
        promotion_ready=promotion_ready([float(v) for v in lifts], gate),
    )


def compare_pattern(
    posts: list[ComparablePost],
    *,
    field: str,
    treatment_value: str,
    control_value: str,
    minimum_similarity: float = 0.62,
    gate: EvidenceGate | None = None,
) -> tuple[list[MatchedPair], ComparativeSummary]:
    pairs = build_matched_pairs(
        posts,
        field=field,
        treatment_value=treatment_value,
        control_value=control_value,
        minimum_similarity=minimum_similarity,
    )
    return pairs, summarize_pairs(
        pairs,
        field=field,
        treatment_value=treatment_value,
        control_value=control_value,
        gate=gate,
    )
