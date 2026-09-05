from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

Role = Literal["hook", "context", "payoff", "reaction", "support", "dead_air", "duplicate", "loop_bridge", "risk"]
VariantKind = Literal[
    "natural",
    "retention",
    "loop",
    "compression",
    "payoff_first",
    "alternate_hook",
    "minimal_text",
    "match_loop",
]

class JobStatus(str, Enum):
    CREATED = "created"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EDITING = "editing"
    QC = "qc"
    EXPORTING = "exporting"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass(frozen=True)
class SourceSpec:
    uri: str
    duration_seconds: float
    filename: str = "raw-video.mp4"
    content_type: str = "video/mp4"
    language: str = "en"
    def __post_init__(self) -> None:
        if not self.uri:
            raise ValueError("source uri is required")
        if self.duration_seconds <= 0:
            raise ValueError("duration_seconds must be > 0")

@dataclass(frozen=True)
class Moment:
    start: float
    end: float
    role: Role
    note: str = ""
    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError("Moment must have 0 <= start < end")

@dataclass(frozen=True)
class LoopScores:
    semantic: float
    visual: float
    audio: float
    hook: float
    payoff: float
    detectability: float
    def __post_init__(self) -> None:
        for value in asdict(self).values():
            if not 0 <= value <= 5:
                raise ValueError("Loop sub-scores must be between 0 and 5")

@dataclass
class VariantPlan:
    kind: VariantKind
    moments: list[Moment] = field(default_factory=list)
    loop_type: str | None = None
    loop_scores: LoopScores | None = None
    notes: list[str] = field(default_factory=list)
    target_duration_seconds: float | None = None

@dataclass
class AnalysisResult:
    premise: str
    transcript: str = ""
    moments: list[Moment] = field(default_factory=list)
    strongest_hook: str = ""
    strongest_payoff: str = ""
    risks: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class QcResult:
    passed: bool
    score: float
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    def __post_init__(self) -> None:
        if not 0 <= self.score <= 100:
            raise ValueError("QC score must be between 0 and 100")

@dataclass
class VariantArtifact:
    kind: VariantKind
    project_id: str | None = None
    composition_id: str | None = None
    share_url: str | None = None
    qc: QcResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class VideoJob:
    job_id: str
    source: SourceSpec
    premise: str = ""
    variants: list[VariantPlan] = field(default_factory=list)
    status: JobStatus = JobStatus.CREATED
    artifacts: list[VariantArtifact] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
    @property
    def source_id(self) -> str:
        return self.source.uri
    @property
    def source_duration(self) -> float:
        return self.source.duration_seconds
    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()
