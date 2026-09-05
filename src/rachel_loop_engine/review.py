from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from .models import VariantKind

REVIEW_MARKER = "RLE_REVIEW_JSON"


@dataclass(frozen=True)
class MediaReview:
    kind: VariantKind
    passed: bool
    overall_score: float
    story_truthfulness: float
    hook_strength: float
    pacing: float
    caption_quality: float | None = None
    audio_quality: float | None = None
    loop_seam: float | None = None
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 0 <= self.overall_score <= 100:
            raise ValueError("overall_score must be between 0 and 100")
        for name in ("story_truthfulness", "hook_strength", "pacing"):
            value = getattr(self, name)
            if not 0 <= value <= 5:
                raise ValueError(f"{name} must be between 0 and 5")
        for name in ("caption_quality", "audio_quality", "loop_seam"):
            value = getattr(self, name)
            if value is not None and not 0 <= value <= 5:
                raise ValueError(f"{name} must be between 0 and 5 when present")


def parse_media_review(agent_response: str, kind: VariantKind) -> MediaReview:
    """Parse the JSON contract emitted by the non-mutating Descript QC prompt."""
    payload = _extract_marked_json(agent_response, REVIEW_MARKER)
    return MediaReview(
        kind=kind,
        passed=bool(payload["passed"]),
        overall_score=float(payload["overall_score"]),
        story_truthfulness=float(payload["story_truthfulness"]),
        hook_strength=float(payload["hook_strength"]),
        pacing=float(payload["pacing"]),
        caption_quality=_optional_float(payload.get("caption_quality")),
        audio_quality=_optional_float(payload.get("audio_quality")),
        loop_seam=_optional_float(payload.get("loop_seam")),
        warnings=[str(x) for x in payload.get("warnings", [])],
        notes=[str(x) for x in payload.get("notes", [])],
    )


def recommend_variant(reviews: list[MediaReview]) -> VariantKind | None:
    """Choose the highest-scoring passing variant with a conservative tie-break."""
    passing = [r for r in reviews if r.passed]
    if not passing:
        return None
    tie_priority: dict[VariantKind, int] = {"natural": 2, "retention": 1, "loop": 0}
    return max(passing, key=lambda r: (r.overall_score, tie_priority[r.kind])).kind


def render_review_card(reviews: list[MediaReview]) -> str:
    recommendation = recommend_variant(reviews)
    title = "# Rachel Loop Engine — Review Card"
    lines = [title, "", f"**Recommended:** {recommendation or 'manual review required'}", ""]
    for review in sorted(reviews, key=lambda r: ("natural", "retention", "loop").index(r.kind)):
        lines.extend(
            [
                f"## {review.kind.title()}",
                f"- Pass: {'yes' if review.passed else 'no'}",
                f"- Overall: {review.overall_score:.1f}/100",
                f"- Truthfulness: {review.story_truthfulness:.1f}/5",
                f"- Hook: {review.hook_strength:.1f}/5",
                f"- Pacing: {review.pacing:.1f}/5",
            ]
        )
        if review.loop_seam is not None:
            lines.append(f"- Loop seam: {review.loop_seam:.1f}/5")
        if review.warnings:
            lines.append("- Warnings: " + "; ".join(review.warnings))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def review_to_dict(review: MediaReview) -> dict[str, Any]:
    return asdict(review)


def _extract_marked_json(text: str, marker: str) -> dict[str, Any]:
    idx = text.find(marker)
    if idx < 0:
        raise ValueError(f"agent response missing marker {marker}")
    tail = text[idx + len(marker):].lstrip(" :\n\t`")
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(tail)
    if not isinstance(obj, dict):
        raise ValueError("review payload must be a JSON object")
    return obj


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)


def review_from_dict(data: dict[str, Any]) -> MediaReview:
    return MediaReview(
        kind=data["kind"],
        passed=bool(data["passed"]),
        overall_score=float(data["overall_score"]),
        story_truthfulness=float(data["story_truthfulness"]),
        hook_strength=float(data["hook_strength"]),
        pacing=float(data["pacing"]),
        caption_quality=_optional_float(data.get("caption_quality")),
        audio_quality=_optional_float(data.get("audio_quality")),
        loop_seam=_optional_float(data.get("loop_seam")),
        warnings=[str(x) for x in data.get("warnings", [])],
        notes=[str(x) for x in data.get("notes", [])],
    )


def reviews_from_job_artifacts(artifacts: list[Any]) -> list[MediaReview]:
    reviews: list[MediaReview] = []
    for artifact in artifacts:
        raw = getattr(artifact, "metadata", {}).get("media_review")
        if isinstance(raw, dict):
            reviews.append(review_from_dict(raw))
    return reviews
