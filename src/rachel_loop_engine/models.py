from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Role = Literal[
    "hook",
    "context",
    "payoff",
    "reaction",
    "support",
    "dead_air",
    "duplicate",
    "loop_bridge",
    "risk",
]

VariantKind = Literal["natural", "retention", "loop"]


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
        for value in (
            self.semantic,
            self.visual,
            self.audio,
            self.hook,
            self.payoff,
            self.detectability,
        ):
            if not 0 <= value <= 5:
                raise ValueError("Loop sub-scores must be between 0 and 5")


@dataclass
class VariantPlan:
    kind: VariantKind
    moments: list[Moment] = field(default_factory=list)
    loop_type: str | None = None
    loop_scores: LoopScores | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class VideoJob:
    source_id: str
    source_duration: float
    premise: str = ""
    variants: list[VariantPlan] = field(default_factory=list)
