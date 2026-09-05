from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from .models import JobStatus, LoopScores, Moment, SourceSpec, VariantPlan, VideoJob

def dump_job(job: VideoJob, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(job), indent=2), encoding="utf-8")
    return p

def load_job(path: str | Path) -> VideoJob:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    source = SourceSpec(**data["source"])
    variants = []
    for raw in data.get("variants", []):
        scores = LoopScores(**raw["loop_scores"]) if raw.get("loop_scores") else None
        moments = [Moment(**m) for m in raw.get("moments", [])]
        variants.append(VariantPlan(kind=raw["kind"], moments=moments, loop_type=raw.get("loop_type"), loop_scores=scores, notes=raw.get("notes", []), target_duration_seconds=raw.get("target_duration_seconds")))
    return VideoJob(job_id=data["job_id"], source=source, premise=data.get("premise", ""), variants=variants, status=JobStatus(data.get("status", "created")), created_at=data.get("created_at", ""), updated_at=data.get("updated_at", ""), metadata=data.get("metadata", {}))
