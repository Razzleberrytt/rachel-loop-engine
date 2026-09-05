from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EvidenceGate:
    minimum_examples: int = 3
    minimum_relative_lift: float = 0.08

def promotion_ready(relative_lifts: list[float], gate: EvidenceGate = EvidenceGate()) -> bool:
    if len(relative_lifts) < gate.minimum_examples:
        return False
    ordered = sorted(relative_lifts)
    n = len(ordered)
    median = ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    return median >= gate.minimum_relative_lift
