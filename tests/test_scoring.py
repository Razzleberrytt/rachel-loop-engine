from rachel_loop_engine.models import LoopScores
from rachel_loop_engine.scoring import loop_decision, loop_score


def test_perfect_loop_scores_five():
    scores = LoopScores(5, 5, 5, 5, 5, 5)
    assert loop_score(scores) == 5.0
    assert loop_decision(loop_score(scores)) == "strong"


def test_decision_thresholds():
    assert loop_decision(4.2) == "strong"
    assert loop_decision(3.6) == "viable"
    assert loop_decision(3.0) == "experimental"
    assert loop_decision(2.999) == "reject"
