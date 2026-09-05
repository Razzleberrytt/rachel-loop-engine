from __future__ import annotations

from .edl import LocalEditPlan, Segment


def retained_segments(
    source_duration: float,
    remove_ranges: list[tuple[float, float]] | None = None,
    *,
    head_trim: float = 0.0,
    tail_trim: float = 0.0,
) -> list[Segment]:
    """Return source intervals left after deterministic removals.

    Ranges are clipped to the source and overlapping removals are merged. AI may
    propose timestamps, but this function decides exactly what source time survives.
    """
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
    """Rotate an EDL so the replay seam is the original source boundary at anchor."""
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


def build_zero_credit_variants(
    source_duration: float,
    *,
    remove_ranges: list[tuple[float, float]] | None = None,
    retention_head_trim: float = 0.0,
    loop_anchor: float | None = None,
) -> dict[str, LocalEditPlan]:
    """Create auditable A/B/C EDLs without invoking an editor AI agent."""
    natural = retained_segments(source_duration, remove_ranges)
    retention = retained_segments(
        source_duration,
        remove_ranges,
        head_trim=retention_head_trim,
    )

    plans: dict[str, LocalEditPlan] = {
        "natural": LocalEditPlan(
            variant="natural",
            segments=natural,
            output_name="A_Natural_Local.mp4",
            notes=["Chronological; deterministic removals only."],
        ),
        "retention": LocalEditPlan(
            variant="retention",
            segments=retention,
            output_name="B_Retention_Local.mp4",
            notes=["Chronological; trims low-value opening before deterministic removals."],
        ),
    }
    if loop_anchor is not None:
        loop_segments = rotate_segments_at_anchor(retention, loop_anchor)
        plans["loop"] = LocalEditPlan(
            variant="loop",
            segments=loop_segments,
            output_name="C_Loop_Local.mp4",
            loop_anchor=loop_anchor,
            notes=[
                "Cyclic timeline rotation; replay seam reconnects the original source at loop_anchor."
            ],
        )
    return plans
