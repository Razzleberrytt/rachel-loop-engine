from rachel_loop_engine.models import LoopScores, Moment, VariantPlan
from rachel_loop_engine.qc import evaluate_plan

def test_good_loop_passes():
    p = VariantPlan(kind="loop", moments=[Moment(0, 3, "hook")], loop_scores=LoopScores(5,4,4,5,4.5,4))
    q = evaluate_plan(p, 10)
    assert q.passed
    assert q.score >= 90

def test_rejected_loop_fails():
    p = VariantPlan(kind="loop", moments=[Moment(0, 3, "hook")], loop_scores=LoopScores(1,1,1,1,1,1))
    assert not evaluate_plan(p, 10).passed
