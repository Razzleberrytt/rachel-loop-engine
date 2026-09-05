from rachel_loop_engine.models import LoopScores
from rachel_loop_engine.scoring import loop_decision, loop_score

def test_scoring():
    s = LoopScores(5,5,5,5,5,5)
    assert loop_score(s) == 5
    assert loop_decision(5) == "strong"
