from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from .models import JobStatus, VideoJob
from .qc import evaluate_plan

class Stage(str, Enum):
    INTAKE = "intake"
    ANALYZE = "analyze"
    PLAN = "plan"
    EDIT = "edit"
    LOOP = "loop"
    QC = "qc"
    EXPORT = "export"
    COMPLETE = "complete"

@dataclass
class JobState:
    job: VideoJob
    stage: Stage = Stage.INTAKE
    error: str | None = None
    events: list[str] = field(default_factory=list)

class RachelLoopPipeline:
    def __init__(self, editor_adapter=None, analyzer_adapter=None):
        self.editor_adapter = editor_adapter
        self.analyzer_adapter = analyzer_adapter
    def dry_run(self, job: VideoJob) -> JobState:
        if not job.source_id:
            return JobState(job=job, error="source_id is required")
        if job.source_duration <= 0:
            return JobState(job=job, error="source_duration must be > 0")
        failures = []
        for plan in job.variants:
            qc = evaluate_plan(plan, job.source_duration)
            failures.extend(qc.failures)
        if failures:
            return JobState(job=job, stage=Stage.QC, error="; ".join(failures), events=["manifest validation failed"])
        return JobState(job=job, stage=Stage.ANALYZE, events=["manifest accepted"])
    def mark(self, job: VideoJob, status: JobStatus) -> VideoJob:
        job.status = status
        job.touch()
        return job
