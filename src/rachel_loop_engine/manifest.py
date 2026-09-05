from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import (
    JobStatus,
    LoopScores,
    Moment,
    QcResult,
    SourceSpec,
    VariantArtifact,
    VariantPlan,
    VideoJob,
)


def dump_job(job: VideoJob, path: str | Path) -> Path:
    """Persist the complete durable job state as human-readable JSON."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(job), indent=2), encoding="utf-8")
    return p


def load_job(path: str | Path) -> VideoJob:
    """Restore a complete job, including QC and published artifacts."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    source = SourceSpec(**data["source"])

    variants: list[VariantPlan] = []
    for raw in data.get("variants", []):
        scores = LoopScores(**raw["loop_scores"]) if raw.get("loop_scores") else None
        moments = [Moment(**m) for m in raw.get("moments", [])]
        variants.append(
            VariantPlan(
                kind=raw["kind"],
                moments=moments,
                loop_type=raw.get("loop_type"),
                loop_scores=scores,
                notes=raw.get("notes", []),
                target_duration_seconds=raw.get("target_duration_seconds"),
            )
        )

    artifacts: list[VariantArtifact] = []
    for raw in data.get("artifacts", []):
        qc = QcResult(**raw["qc"]) if raw.get("qc") else None
        artifacts.append(
            VariantArtifact(
                kind=raw["kind"],
                project_id=raw.get("project_id"),
                composition_id=raw.get("composition_id"),
                share_url=raw.get("share_url"),
                qc=qc,
                metadata=raw.get("metadata", {}),
            )
        )

    return VideoJob(
        job_id=data["job_id"],
        source=source,
        premise=data.get("premise", ""),
        variants=variants,
        status=JobStatus(data.get("status", "created")),
        artifacts=artifacts,
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
        metadata=data.get("metadata", {}),
    )
