from __future__ import annotations
from .models import LoopScores

WEIGHTS = {"semantic": 0.20, "visual": 0.15, "audio": 0.15, "hook": 0.20, "payoff": 0.20, "detectability": 0.10}

def loop_score(scores: LoopScores) -> float:
    return round(sum(getattr(scores, k) * w for k, w in WEIGHTS.items()), 3)

def loop_decision(score: float) -> str:
    if not 0 <= score <= 5:
        raise ValueError("score must be between 0 and 5")
    if score >= 4.2: return "strong"
    if score >= 3.6: return "viable"
    if score >= 3.0: return "experimental"
    return "reject"
