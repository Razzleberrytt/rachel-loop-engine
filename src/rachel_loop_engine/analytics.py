from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class VideoMetrics:
    views: int
    video_duration_seconds: float
    average_watch_seconds: float | None = None
    average_percentage_viewed: float | None = None
    completion_rate: float | None = None
    replay_rate: float | None = None
    share_rate: float | None = None
    save_rate: float | None = None

    def __post_init__(self) -> None:
        if self.views < 0:
            raise ValueError("views must be >= 0")
        if self.video_duration_seconds <= 0:
            raise ValueError("video_duration_seconds must be > 0")
        for name in (
            "average_watch_seconds",
            "average_percentage_viewed",
            "completion_rate",
            "replay_rate",
            "share_rate",
            "save_rate",
        ):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} must be >= 0")

    @property
    def average_watch_ratio(self) -> float | None:
        if self.average_watch_seconds is not None:
            return self.average_watch_seconds / self.video_duration_seconds
        return self.average_percentage_viewed


@dataclass(frozen=True)
class PerformanceSnapshot:
    job_id: str
    variant: str
    platform: str
    captured_at: str
    metrics: VideoMetrics
    video_id: str | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    saves: int | None = None
    follows_attributed: int | None = None

    def __post_init__(self) -> None:
        if not self.job_id.strip():
            raise ValueError("job_id is required")
        if not self.variant.strip():
            raise ValueError("variant is required")
        if not self.platform.strip():
            raise ValueError("platform is required")
        if not self.captured_at.strip():
            raise ValueError("captured_at is required")
        for name in ("likes", "comments", "shares", "saves", "follows_attributed"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} must be >= 0")

    @property
    def engagement_per_view(self) -> float | None:
        if self.metrics.views <= 0:
            return None
        counts = [self.likes, self.comments, self.shares, self.saves]
        if all(value is None for value in counts):
            return None
        return sum(value or 0 for value in counts) / self.metrics.views

    @property
    def shares_per_1000_views(self) -> float | None:
        if self.shares is None or self.metrics.views <= 0:
            return None
        return self.shares * 1000 / self.metrics.views

    def to_record(self) -> dict[str, object]:
        record = asdict(self)
        record["derived"] = {
            "average_watch_ratio": self.metrics.average_watch_ratio,
            "retention_index": retention_index(self.metrics),
            "engagement_per_view": self.engagement_per_view,
            "shares_per_1000_views": self.shares_per_1000_views,
        }
        return record


def retention_index(m: VideoMetrics) -> float | None:
    fields = [
        (m.average_watch_ratio, 0.40),
        (m.completion_rate, 0.30),
        (m.replay_rate, 0.20),
        (m.share_rate, 0.07),
        (m.save_rate, 0.03),
    ]
    present = [(v, w) for v, w in fields if v is not None]
    if not present:
        return None
    total_weight = sum(w for _, w in present)
    return round(sum(float(v) * w for v, w in present) / total_weight, 4)


def relative_lift(candidate: VideoMetrics, baseline: VideoMetrics) -> float | None:
    c = retention_index(candidate)
    b = retention_index(baseline)
    if c is None or b in (None, 0):
        return None
    return round((c - b) / b, 4)


def append_snapshot(path: str | Path, snapshot: PerformanceSnapshot) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(snapshot.to_record(), sort_keys=True) + "\n")
    return target


def load_snapshots(path: str | Path) -> list[dict[str, object]]:
    target = Path(path)
    if not target.exists():
        return []
    snapshots: list[dict[str, object]] = []
    with target.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                snapshots.append(json.loads(line))
    return snapshots


def latest_snapshot(path: str | Path) -> dict[str, object] | None:
    snapshots = load_snapshots(path)
    return snapshots[-1] if snapshots else None
