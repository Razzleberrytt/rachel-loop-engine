from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import VideoJob


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


class RachelLoopPipeline:
    """Thin orchestration shell.

    External editors/transcribers should be adapters, not embedded directly in
    the planner. This keeps the creative brain portable across services.
    """

    def __init__(self, editor_adapter=None, analyzer_adapter=None):
        self.editor_adapter = editor_adapter
        self.analyzer_adapter = analyzer_adapter

    def dry_run(self, job: VideoJob) -> JobState:
        """Validate that a job can enter the pipeline without touching media."""
        if not job.source_id:
            return JobState(job=job, error="source_id is required")
        if job.source_duration <= 0:
            return JobState(job=job, error="source_duration must be > 0")
        return JobState(job=job, stage=Stage.ANALYZE)
