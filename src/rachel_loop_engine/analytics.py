from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class VideoMetrics:
    views: int
    video_duration_seconds: float
    average_watch_seconds: float | None = None
    completion_rate: float | None = None
    replay_rate: float | None = None
    share_rate: float | None = None
    save_rate: float | None = None
    @property
    def average_watch_ratio(self) -> float | None:
        if self.average_watch_seconds is None or self.video_duration_seconds <= 0:
            return None
        return self.average_watch_seconds / self.video_duration_seconds

def retention_index(m: VideoMetrics) -> float | None:
    fields = [(m.average_watch_ratio, 0.40), (m.completion_rate, 0.30), (m.replay_rate, 0.20), (m.share_rate, 0.07), (m.save_rate, 0.03)]
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
