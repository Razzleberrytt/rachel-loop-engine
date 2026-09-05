from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .adapters.ffmpeg import FfmpegAdapter
from .analytics import PerformanceSnapshot, VideoMetrics, append_snapshot
from .edl import dump_plan, load_plan
from .manifest import dump_job, load_job
from .models import SourceSpec, VideoJob
from .pipeline import RachelLoopPipeline
from .planner import build_zero_credit_variants
from .review import render_review_card, reviews_from_job_artifacts


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

    plan = sub.add_parser("plan-local", help="build deterministic A/B/C EDLs without editor AI credits")
    plan.add_argument("manifest")
    plan.add_argument("--remove", type=_time_range, action="append", default=[], metavar="START:END")
    plan.add_argument("--head-trim", type=float, default=0.0)
    plan.add_argument("--loop-anchor", type=float)
    plan.add_argument("--out-dir", default="local-plans")

    render = sub.add_parser("render-local", help="render one EDL with FFmpeg; no editor AI credits")
    render.add_argument("manifest")
    render.add_argument("plan")
    render.add_argument("source_path")
    render.add_argument("--out")
    render.add_argument("--preset", default="veryfast")
    render.add_argument("--crf", type=int, default=18)

    metrics = sub.add_parser("record-metrics", help="append a timestamped post-performance snapshot")
    metrics.add_argument("manifest")
    metrics.add_argument("--platform", required=True)
    metrics.add_argument("--variant", required=True)
    metrics.add_argument("--views", type=int, required=True)
    metrics.add_argument("--video-id")
    metrics.add_argument("--captured-at")
    metrics.add_argument("--average-watch", type=float)
    metrics.add_argument("--apv", type=_ratio, help="average percentage viewed: 2.15 or 215%%")
    metrics.add_argument("--completion", type=_ratio)
    metrics.add_argument("--replay-rate", type=_ratio)
    metrics.add_argument("--likes", type=int)
    metrics.add_argument("--comments", type=int)
    metrics.add_argument("--shares", type=int)
    metrics.add_argument("--saves", type=int)
    metrics.add_argument("--follows", type=int)
    metrics.add_argument("--out", default="analytics/performance-snapshots.jsonl")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "new-job":
        job = VideoJob(
            job_id=str(uuid.uuid4()),
            source=SourceSpec(uri=args.source_uri, duration_seconds=args.duration),
            premise=args.premise,
        )
        print(dump_job(job, args.out))
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
        plans = build_zero_credit_variants(
            job.source_duration,
            remove_ranges=args.remove,
            retention_head_trim=args.head_trim,
            loop_anchor=args.loop_anchor,
        )
        out_dir = Path(args.out_dir)
        written = {
            kind: str(dump_plan(plan, out_dir / f"{kind}.json"))
            for kind, plan in plans.items()
        }
        print(json.dumps(written, indent=2))
        return 0
    if args.command == "render-local":
        plan = load_plan(args.plan)
        output = Path(args.out) if args.out else Path(plan.output_name)
        ref = FfmpegAdapter().render(
            args.source_path,
            output,
            plan,
            source_duration=job.source_duration,
            preset=args.preset,
            crf=args.crf,
        )
        print(json.dumps(asdict(ref), indent=2))
        return 0
    if args.command == "record-metrics":
        views = args.views
        shares = args.shares
        saves = args.saves
        metrics = VideoMetrics(
            views=views,
            video_duration_seconds=job.source_duration,
            average_watch_seconds=args.average_watch,
            average_percentage_viewed=args.apv,
            completion_rate=args.completion,
            replay_rate=args.replay_rate,
            share_rate=(shares / views) if shares is not None and views > 0 else None,
            save_rate=(saves / views) if saves is not None and views > 0 else None,
        )
        captured_at = args.captured_at or datetime.now(timezone.utc).isoformat()
        snapshot = PerformanceSnapshot(
            job_id=job.job_id,
            variant=args.variant,
            platform=args.platform,
            captured_at=captured_at,
            video_id=args.video_id,
            metrics=metrics,
            likes=args.likes,
            comments=args.comments,
            shares=shares,
            saves=saves,
            follows_attributed=args.follows,
        )
        target = append_snapshot(args.out, snapshot)
        payload = snapshot.to_record()
        payload["snapshot_file"] = str(target)
        print(json.dumps(payload, indent=2))
        return 0

    state = RachelLoopPipeline().dry_run(job)
    print(json.dumps({"stage": state.stage.value, "error": state.error, "events": state.events}, indent=2))
    return 1 if state.error else 0


if __name__ == "__main__":
    raise SystemExit(main())
