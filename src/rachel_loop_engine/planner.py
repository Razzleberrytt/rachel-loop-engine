from __future__ import annotations

from .edl import LocalEditPlan, Segment, TextOverlay


def retained_segments(
    source_duration: float,
    remove_ranges: list[tuple[float, float]] | None = None,
    *,
    head_trim: float = 0.0,
    tail_trim: float = 0.0,
) -> list[Segment]:
    if source_duration <= 0:
        raise ValueError("source_duration must be > 0")
    start = max(0.0, float(head_trim))
    end = min(source_duration, source_duration - max(0.0, float(tail_trim)))
    if end <= start:
        raise ValueError("head/tail trims remove the entire source")
    clipped: list[tuple[float, float]] = []
    for raw_start, raw_end in remove_ranges or []:
        a = max(start, float(raw_start))
        b = min(end, float(raw_end))
        if b > a:
            clipped.append((a, b))
    clipped.sort()
    merged: list[list[float]] = []
    for a, b in clipped:
        if not merged or a > merged[-1][1]:
            merged.append([a, b])
        else:
            merged[-1][1] = max(merged[-1][1], b)
    result: list[Segment] = []
    cursor = start
    for a, b in merged:
        if a > cursor:
            result.append(Segment(cursor, a, label="retained"))
        cursor = max(cursor, b)
    if cursor < end:
        result.append(Segment(cursor, end, label="retained"))
    if not result:
        raise ValueError("remove_ranges remove the entire source")
    return result


def rotate_segments_at_anchor(segments: list[Segment], anchor: float) -> list[Segment]:
    if not segments:
        raise ValueError("segments are required")
    anchor = float(anchor)
    split: list[Segment] = []
    first_after_anchor: int | None = None
    for seg in segments:
        if seg.source_start < anchor < seg.source_end:
            split.append(Segment(seg.source_start, anchor, label=seg.label, zoom=seg.zoom))
            first_after_anchor = len(split)
            split.append(Segment(anchor, seg.source_end, label=seg.label, zoom=seg.zoom))
        elif abs(anchor - seg.source_start) <= 1e-9:
            first_after_anchor = len(split)
            split.append(seg)
        elif abs(anchor - seg.source_end) <= 1e-9:
            split.append(seg)
            first_after_anchor = len(split) % (len(split) + 1)
        else:
            split.append(seg)
    if first_after_anchor is None:
        raise ValueError("loop anchor must lie in a retained segment")
    first_after_anchor %= len(split)
    return split[first_after_anchor:] + split[:first_after_anchor]


def move_range_to_front(segments: list[Segment], focus: tuple[float, float]) -> list[Segment]:
    """Move one retained source range to the front without duplicating content."""
    a, b = focus
    if a < 0 or b <= a:
        raise ValueError("focus range must satisfy 0 <= start < end")
    focus_parts: list[Segment] = []
    remainder: list[Segment] = []
    for seg in segments:
        if b <= seg.source_start or a >= seg.source_end:
            remainder.append(seg)
            continue
        left = max(seg.source_start, a)
        right = min(seg.source_end, b)
        if seg.source_start < left:
            remainder.append(Segment(seg.source_start, left, label=seg.label, zoom=seg.zoom))
        focus_parts.append(Segment(left, right, label="focus_hook", zoom=seg.zoom))
        if right < seg.source_end:
            remainder.append(Segment(right, seg.source_end, label=seg.label, zoom=seg.zoom))
    if not focus_parts:
        raise ValueError("focus range does not intersect retained footage")
    return focus_parts + remainder


def build_zero_credit_variants(
    source_duration: float,
    *,
    remove_ranges: list[tuple[float, float]] | None = None,
    retention_head_trim: float = 0.0,
    loop_anchor: float | None = None,
) -> dict[str, LocalEditPlan]:
    natural = retained_segments(source_duration, remove_ranges)
    retention = retained_segments(source_duration, remove_ranges, head_trim=retention_head_trim)
    plans: dict[str, LocalEditPlan] = {
        "natural": LocalEditPlan("natural", natural, "A_Natural_Local.mp4", notes=["Chronological; deterministic removals only."]),
        "retention": LocalEditPlan("retention", retention, "B_Retention_Local.mp4", notes=["Chronological; trims low-value opening before deterministic removals."]),
    }
    if loop_anchor is not None:
        plans["loop"] = LocalEditPlan(
            "loop", rotate_segments_at_anchor(retention, loop_anchor), "C_Loop_Local.mp4",
            loop_anchor=loop_anchor,
            notes=["Cyclic timeline rotation; replay seam reconnects the original source at loop_anchor."],
        )
    return plans


def build_hypothesis_variants(
    source_duration: float,
    *,
    remove_ranges: list[tuple[float, float]] | None = None,
    compression_remove_ranges: list[tuple[float, float]] | None = None,
    retention_head_trim: float = 0.0,
    loop_anchor: float | None = None,
    loop_score: float | None = None,
    payoff_range: tuple[float, float] | None = None,
    alternate_hook_range: tuple[float, float] | None = None,
    primary_text: str | None = None,
    include_no_text_variant: bool = True,
) -> dict[str, LocalEditPlan]:
    """Generate only variants backed by an explicit creative hypothesis."""
    plans = build_zero_credit_variants(
        source_duration,
        remove_ranges=remove_ranges,
        retention_head_trim=retention_head_trim,
        loop_anchor=loop_anchor,
    )
    if loop_anchor is not None and "loop" in plans:
        plans["loop"].metadata.update({"loop_type": "source_contiguous_rotation", "loop_score": loop_score})

    if compression_remove_ranges:
        combined = list(remove_ranges or []) + list(compression_remove_ranges)
        compressed = retained_segments(source_duration, combined, head_trim=retention_head_trim)
        if _signature(compressed) != _signature(plans["retention"].segments):
            plans["compression"] = LocalEditPlan(
                "compression", compressed, "D_Compression_Local.mp4",
                notes=["Tests whether additional dead-time compression improves retention."],
                metadata={"hypothesis": "compression"},
            )

    if payoff_range is not None:
        reordered = move_range_to_front(plans["retention"].segments, payoff_range)
        if _signature(reordered) != _signature(plans["retention"].segments):
            plans["payoff_first"] = LocalEditPlan(
                "payoff_first", reordered, "D_Payoff_First_Local.mp4",
                notes=["Opens on a genuine payoff/reaction, then returns to remaining context."],
                metadata={"hook_type": "payoff_first", "hypothesis": "payoff_first"},
            )

    if alternate_hook_range is not None:
        reordered = move_range_to_front(plans["retention"].segments, alternate_hook_range)
        if _signature(reordered) != _signature(plans["retention"].segments):
            plans["alternate_hook"] = LocalEditPlan(
                "alternate_hook", reordered, "E_Alternate_Hook_Local.mp4",
                notes=["Tests a second truthful opening without changing the retained story."],
                metadata={"hook_type": "alternate", "hypothesis": "alternate_hook"},
            )

    if primary_text and primary_text.strip():
        for key in ("retention", "loop"):
            if key in plans:
                plan = plans[key]
                end = min(2.2, plan.output_duration)
                if end > 0.05:
                    plan.text_overlays = [TextOverlay(primary_text.strip(), 0.0, end)]
                    plan.metadata.update({"caption_style": "single_phrase", "text_overlay": "present"})
        if include_no_text_variant:
            base = plans["retention"]
            plans["minimal_text"] = LocalEditPlan(
                "minimal_text", list(base.segments), "F_No_Text_Local.mp4",
                notes=["Matched no-text control for the primary on-screen phrase."],
                metadata={"caption_style": "none", "text_overlay": "none", "hypothesis": "text_vs_no_text"},
            )
    return plans


def build_match_loop_plan(start_seconds: float, end_seconds: float, *, score: float | None = None) -> LocalEditPlan:
    if start_seconds < 0 or end_seconds <= start_seconds:
        raise ValueError("match loop must satisfy 0 <= start < end")
    return LocalEditPlan(
        "match_loop",
        [Segment(start_seconds, end_seconds, label="visual_match_loop")],
        "C2_Visual_Match_Loop.mp4",
        notes=["Non-contiguous visual-match loop; must pass finished-media seam QC before posting."],
        metadata={"loop_type": "visual_match_pair", "loop_score": score, "hypothesis": "visual_match_loop"},
    )


def _signature(segments: list[Segment]) -> tuple[tuple[float, float], ...]:
    return tuple((round(s.source_start, 6), round(s.source_end, 6)) for s in segments)
