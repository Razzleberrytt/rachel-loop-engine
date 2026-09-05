from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import asdict

from .manifest import dump_job, load_job
from .models import SourceSpec, VideoJob
from .pipeline import RachelLoopPipeline
from .review import render_review_card, reviews_from_job_artifacts


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

    state = RachelLoopPipeline().dry_run(job)
    print(json.dumps({"stage": state.stage.value, "error": state.error, "events": state.events}, indent=2))
    return 1 if state.error else 0


if __name__ == "__main__":
    raise SystemExit(main())
