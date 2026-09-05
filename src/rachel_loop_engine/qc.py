from __future__ import annotations
from .models import QcResult, VariantPlan
from .scoring import loop_decision, loop_score

def evaluate_plan(plan: VariantPlan, source_duration: float) -> QcResult:
    failures: list[str] = []
    warnings: list[str] = []
    score = 100.0
    if not plan.moments:
        failures.append("variant has no selected moments")
        score -= 50
    for moment in plan.moments:
        if moment.end > source_duration + 1e-6:
            failures.append(f"moment exceeds source duration: {moment.start}-{moment.end}")
            score -= 20
        if moment.role == "dead_air":
            warnings.append("dead_air moment remains in plan")
            score -= 8
    if plan.kind == "loop":
        if plan.loop_scores is None:
            failures.append("loop variant is missing loop scores")
            score -= 35
        else:
            decision = loop_decision(loop_score(plan.loop_scores))
            if decision == "reject":
                failures.append("loop score is below publish threshold")
                score -= 35
            elif decision == "experimental":
                warnings.append("loop is experimental; prefer A/B review before publishing")
                score -= 10
    return QcResult(passed=not failures, score=max(0.0, round(score, 1)), failures=failures, warnings=warnings)
