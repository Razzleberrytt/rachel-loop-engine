from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .adapters.ffmpeg import FfmpegAdapter
from .analytics import (
    EvidenceProvenance,
    PerformanceSnapshot,
    VideoMetrics,
    append_snapshot,
    screenshot_provenance,
)
from .edl import dump_plan, load_plan
from .experiments import ComparablePost, compare_pattern
from .manifest import dump_job, load_job
from .media import MediaProbe
from .models import SourceSpec, VideoJob
from .pipeline import RachelLoopPipeline
from .planner import build_hypothesis_variants, build_zero_credit_variants
from .render_qc import RenderInspector
from .review import render_review_card, reviews_from_job_artifacts
from .seam_hunter import SeamHunter
from .treatment import AutoTreatmentConfig, OneButtonTreatmentRunner


def _time_range(value: str) -> tuple[float, float]:
    try:
        left, right = value.split(":", 1)
        start, end = float(left), float(right)
    except Exception as exc:
        raise argparse.ArgumentTypeError("range must be START:END in seconds") from exc
    if start < 0 or end <= start:
        raise argparse.ArgumentTypeError("range must satisfy 0 <= START < END")
    return start, end


def _ratio(value: str) -> float:
    try:
        raw = value.strip()
        ratio = float(raw[:-1]) / 100 if raw.endswith("%") else float(raw)
    except Exception as exc:
        raise argparse.ArgumentTypeError("ratio must be a decimal (2.15) or percent (215%)") from exc
    if ratio < 0:
        raise argparse.ArgumentTypeError("ratio must be >= 0")
    return ratio


def _bool_choice(value: str) -> bool | None:
    lowered = value.casefold()
    if lowered in {"yes", "true", "1"}: return True
    if lowered in {"no", "false", "0"}: return False
    if lowered in {"auto", "unknown"}: return None
    raise argparse.ArgumentTypeError("expected yes, no, or auto")


def _add_metrics_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--platform", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--views", type=int, required=True)
    parser.add_argument("--video-id")
    parser.add_argument("--captured-at")
    parser.add_argument("--post-timestamp")
    parser.add_argument("--average-watch", type=float)
    parser.add_argument("--apv", type=_ratio, help="average percentage viewed: 2.15 or 215%%")
    parser.add_argument("--completion", type=_ratio)
    parser.add_argument("--replay-rate", type=_ratio)
    parser.add_argument("--likes", type=int)
    parser.add_argument("--comments", type=int)
    parser.add_argument("--shares", type=int)
    parser.add_argument("--saves", type=int)
    parser.add_argument("--follows", type=int)
    parser.add_argument("--out", default="analytics/performance-snapshots.jsonl")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rle", description="Rachel Loop Engine")
    sub = p.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new-job", help="create a job manifest")
    new.add_argument("source_uri")
    new.add_argument("--duration", type=float, required=True)
    new.add_argument("--premise", default="")
    new.add_argument("--out", default="job.json")

    dry = sub.add_parser("dry-run", help="validate a job without editing media")
    dry.add_argument("manifest")
    show = sub.add_parser("show", help="print normalized job JSON")
    show.add_argument("manifest")
    card = sub.add_parser("review-card", help="render media-aware QC stored in a completed job")
    card.add_argument("manifest")

    plan = sub.add_parser("plan-local", help="build deterministic core A/B/C EDLs")
    plan.add_argument("manifest")
    plan.add_argument("--remove", type=_time_range, action="append", default=[], metavar="START:END")
    plan.add_argument("--head-trim", type=float, default=0.0)
    plan.add_argument("--loop-anchor", type=float)
    plan.add_argument("--out-dir", default="local-plans")

    smart = sub.add_parser("plan-smart", help="build hypothesis-driven local variants")
    smart.add_argument("manifest")
    smart.add_argument("--remove", type=_time_range, action="append", default=[], metavar="START:END")
    smart.add_argument("--compression-remove", type=_time_range, action="append", default=[], metavar="START:END")
    smart.add_argument("--head-trim", type=float, default=0.0)
    smart.add_argument("--loop-anchor", type=float)
    smart.add_argument("--loop-score", type=float)
    smart.add_argument("--payoff", type=_time_range)
    smart.add_argument("--alternate-hook", type=_time_range)
    smart.add_argument("--text")
    smart.add_argument("--no-no-text-control", action="store_true")
    smart.add_argument("--out-dir", default="smart-plans")

    render = sub.add_parser("render-local", help="render one EDL with FFmpeg")
    render.add_argument("manifest")
    render.add_argument("plan")
    render.add_argument("source_path")
    render.add_argument("--out")
    render.add_argument("--preset", default="veryfast")
    render.add_argument("--crf", type=int, default=18)

    hunt = sub.add_parser("hunt-seams", help="rank source-contiguous and visual-match loop candidates")
    hunt.add_argument("source_path")
    hunt.add_argument("--step", type=float, default=.25)
    hunt.add_argument("--top", type=int, default=5)
    hunt.add_argument("--match-pairs", action="store_true")
    hunt.add_argument("--preview-dir")

    inspect = sub.add_parser("inspect-render", help="mechanically QC a finished render")
    inspect.add_argument("render_path")
    inspect.add_argument("--duration", type=float)
    inspect.add_argument("--width", type=int, default=1080)
    inspect.add_argument("--height", type=int, default=1920)
    inspect.add_argument("--fps", type=float, default=30)
    inspect.add_argument("--audio", type=_bool_choice, default=None)
    inspect.add_argument("--no-artifact-scan", action="store_true")

    metrics = sub.add_parser("record-metrics", help="append a timestamped post-performance snapshot")
    metrics.add_argument("manifest")
    _add_metrics_args(metrics)

    screenshot = sub.add_parser("record-screenshot-metrics", help="append metrics extracted from an analytics screenshot")
    screenshot.add_argument("manifest")
    screenshot.add_argument("screenshot_path")
    screenshot.add_argument("--extraction-method", default="chatgpt_vision")
    screenshot.add_argument("--confidence", type=float)
    screenshot.add_argument("--screenshot-captured-at")
    screenshot.add_argument("--provenance-notes")
    _add_metrics_args(screenshot)

    compare = sub.add_parser("compare-pattern", help="matched-pair comparison across comparable post records")
    compare.add_argument("posts_json")
    compare.add_argument("--field", required=True)
    compare.add_argument("--treatment", required=True)
    compare.add_argument("--control", required=True)
    compare.add_argument("--min-similarity", type=float, default=.62)

    treat = sub.add_parser("treat-local", help="one-button local treatment with seam hunt, variants, QC and registration")
    treat.add_argument("manifest")
    treat.add_argument("source_path")
    treat.add_argument("--output-dir", default="rle-output")
    treat.add_argument("--remove", type=_time_range, action="append", default=[], metavar="START:END")
    treat.add_argument("--compression-remove", type=_time_range, action="append", default=[], metavar="START:END")
    treat.add_argument("--head-trim", type=float, default=0.0)
    treat.add_argument("--loop-anchor", type=float)
    treat.add_argument("--payoff", type=_time_range)
    treat.add_argument("--alternate-hook", type=_time_range)
    treat.add_argument("--text")
    treat.add_argument("--no-auto-loop", action="store_true")
    treat.add_argument("--no-match-loop", action="store_true")
    treat.add_argument("--no-no-text-control", action="store_true")
    treat.add_argument("--content-class", default="unknown")
    treat.add_argument("--hook-type", default="unknown")
    treat.add_argument("--motion-level", default="unknown")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "new-job":
        job = VideoJob(job_id=str(uuid.uuid4()), source=SourceSpec(uri=args.source_uri, duration_seconds=args.duration), premise=args.premise)
        print(dump_job(job, args.out))
        return 0

    if args.command == "hunt-seams":
        probe = MediaProbe()
        info = probe.probe(args.source_path)
        hunter = SeamHunter(probe=probe)
        rotations = hunter.hunt(
            args.source_path, duration_seconds=info.duration_seconds, fps=info.fps or 30,
            has_audio=info.has_audio, step_seconds=args.step, top_n=args.top,
        )
        payload: dict[str, object] = {"media": asdict(info), "rotation_candidates": [c.to_record() for c in rotations]}
        if args.match_pairs:
            pairs = hunter.hunt_match_pairs(args.source_path, duration_seconds=info.duration_seconds, top_n=args.top)
            payload["match_candidates"] = [c.to_record() for c in pairs]
        if args.preview_dir and rotations:
            adapter = FfmpegAdapter(probe=probe)
            preview_dir = Path(args.preview_dir)
            preview_paths = []
            for index, candidate in enumerate(rotations[: min(3, len(rotations))], start=1):
                loop = build_zero_credit_variants(info.duration_seconds, loop_anchor=candidate.anchor_seconds)["loop"]
                single = preview_dir / f"candidate_{index}_single.mp4"
                ref = adapter.render(args.source_path, single, loop, source_duration=info.duration_seconds, has_audio=info.has_audio)
                repeated = preview_dir / f"candidate_{index}_3cycles.mp4"
                adapter.repeat_video(ref.path, repeated, cycles=3, duration_seconds=ref.expected_duration, has_audio=ref.has_audio)
                preview_paths.append(str(repeated))
            payload["three_cycle_previews"] = preview_paths
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "inspect-render":
        inspection = RenderInspector().inspect(
            args.render_path,
            expected_duration=args.duration,
            expected_width=args.width,
            expected_height=args.height,
            expected_fps=args.fps,
            expected_audio=args.audio,
            scan_artifacts=not args.no_artifact_scan,
        )
        print(json.dumps(inspection.to_record(), indent=2))
        return 0 if inspection.passed else 1

    if args.command == "compare-pattern":
        raw_posts = json.loads(Path(args.posts_json).read_text(encoding="utf-8"))
        posts = [_comparable_post(item) for item in raw_posts]
        pairs, summary = compare_pattern(
            posts, field=args.field, treatment_value=args.treatment, control_value=args.control,
            minimum_similarity=args.min_similarity,
        )
        print(json.dumps({"pairs": [asdict(pair) for pair in pairs], "summary": summary.to_record()}, indent=2))
        return 0

    job = load_job(args.manifest)
    if args.command == "show":
        print(json.dumps(asdict(job), indent=2))
        return 0
    if args.command == "review-card":
        reviews = reviews_from_job_artifacts(job.artifacts)
        if not reviews:
            print("No media-aware reviews are stored in this job.")
            return 1
        print(render_review_card(reviews), end="")
        return 0
    if args.command == "plan-local":
        plans = build_zero_credit_variants(job.source_duration, remove_ranges=args.remove, retention_head_trim=args.head_trim, loop_anchor=args.loop_anchor)
        return _write_plans(plans, args.out_dir)
    if args.command == "plan-smart":
        plans = build_hypothesis_variants(
            job.source_duration, remove_ranges=args.remove, compression_remove_ranges=args.compression_remove,
            retention_head_trim=args.head_trim, loop_anchor=args.loop_anchor, loop_score=args.loop_score,
            payoff_range=args.payoff, alternate_hook_range=args.alternate_hook, primary_text=args.text,
            include_no_text_variant=not args.no_no_text_control,
        )
        return _write_plans(plans, args.out_dir)
    if args.command == "render-local":
        plan = load_plan(args.plan)
        output = Path(args.out) if args.out else Path(plan.output_name)
        ref = FfmpegAdapter().render(args.source_path, output, plan, source_duration=job.source_duration, preset=args.preset, crf=args.crf)
        print(json.dumps(asdict(ref), indent=2))
        return 0
    if args.command in {"record-metrics", "record-screenshot-metrics"}:
        provenance: EvidenceProvenance | None = None
        if args.command == "record-screenshot-metrics":
            provenance = screenshot_provenance(
                args.screenshot_path,
                extraction_method=args.extraction_method,
                extraction_confidence=args.confidence,
                source_captured_at=args.screenshot_captured_at,
                notes=args.provenance_notes,
            )
        else:
            provenance = EvidenceProvenance(source_kind="manual_entry", extraction_method="rle_cli")
        snapshot = _snapshot_from_args(job, args, provenance)
        target = append_snapshot(args.out, snapshot)
        payload = snapshot.to_record()
        payload["snapshot_file"] = str(target)
        print(json.dumps(payload, indent=2))
        return 0
    if args.command == "treat-local":
        config = AutoTreatmentConfig(
            remove_ranges=args.remove,
            compression_remove_ranges=args.compression_remove,
            retention_head_trim=args.head_trim,
            loop_anchor=args.loop_anchor,
            payoff_range=args.payoff,
            alternate_hook_range=args.alternate_hook,
            primary_text=args.text,
            include_no_text_variant=not args.no_no_text_control,
            auto_hunt_loop=not args.no_auto_loop,
            include_match_loop=not args.no_match_loop,
            content_class=args.content_class,
            hook_type=args.hook_type,
            motion_level=args.motion_level,
        )
        result = OneButtonTreatmentRunner().run(job, source_path=args.source_path, output_dir=args.output_dir, config=config)
        dump_job(job, args.manifest)
        print(json.dumps({
            "recommended_variant": result.recommended_variant,
            "ranking": result.ranking,
            "loop_preview": result.loop_preview,
            "social_copy": result.social_copy.to_record(),
            "report_path": result.report_path,
            "warnings": result.warnings,
        }, indent=2))
        return 0 if result.local.renders else 1

    state = RachelLoopPipeline().dry_run(job)
    print(json.dumps({"stage": state.stage.value, "error": state.error, "events": state.events}, indent=2))
    return 1 if state.error else 0


def _write_plans(plans, out_dir: str) -> int:
    target = Path(out_dir)
    written = {kind: str(dump_plan(plan, target / f"{kind}.json")) for kind, plan in plans.items()}
    print(json.dumps(written, indent=2))
    return 0


def _snapshot_from_args(job: VideoJob, args, provenance: EvidenceProvenance) -> PerformanceSnapshot:
    views = args.views
    shares = args.shares
    saves = args.saves
    fingerprints = job.metadata.get("creative_fingerprints") or {}
    fingerprint = fingerprints.get(args.variant) if isinstance(fingerprints, dict) else None
    duration = job.source_duration
    fingerprint_id = None
    if isinstance(fingerprint, dict):
        duration = float(fingerprint.get("duration_seconds") or duration)
        fingerprint_id = str(fingerprint.get("fingerprint_id") or "") or None
    metrics = VideoMetrics(
        views=views,
        video_duration_seconds=duration,
        average_watch_seconds=args.average_watch,
        average_percentage_viewed=args.apv,
        completion_rate=args.completion,
        replay_rate=args.replay_rate,
        share_rate=(shares / views) if shares is not None and views > 0 else None,
        save_rate=(saves / views) if saves is not None and views > 0 else None,
    )
    return PerformanceSnapshot(
        job_id=job.job_id,
        variant=args.variant,
        platform=args.platform,
        captured_at=args.captured_at or datetime.now(timezone.utc).isoformat(),
        post_timestamp=args.post_timestamp,
        video_id=args.video_id,
        metrics=metrics,
        likes=args.likes,
        comments=args.comments,
        shares=shares,
        saves=saves,
        follows_attributed=args.follows,
        creative_fingerprint_id=fingerprint_id,
        creative_fingerprint=fingerprint if isinstance(fingerprint, dict) else None,
        provenance=provenance,
    )


def _comparable_post(data: dict[str, object]) -> ComparablePost:
    raw_metrics = data.get("metrics")
    if not isinstance(raw_metrics, dict):
        raise ValueError("each comparable post requires a metrics object")
    metrics = VideoMetrics(**raw_metrics)
    return ComparablePost(
        post_id=str(data["post_id"]),
        platform=str(data["platform"]),
        content_class=str(data.get("content_class", "unknown")),
        duration_seconds=float(data.get("duration_seconds") or metrics.video_duration_seconds),
        metrics=metrics,
        hook_type=str(data.get("hook_type", "unknown")),
        loop_type=str(data.get("loop_type", "none")),
        caption_style=str(data.get("caption_style", "unknown")),
        audio_mode=str(data.get("audio_mode", "unknown")),
        motion_level=str(data.get("motion_level", "unknown")),
        posted_hour=float(data["posted_hour"]) if data.get("posted_hour") is not None else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
