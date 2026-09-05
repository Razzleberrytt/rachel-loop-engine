from rachel_loop_engine.models import SourceSpec, VideoJob
from rachel_loop_engine.pipeline import RachelLoopPipeline, Stage

def test_dry_run_accepts_minimal_job():
    job = VideoJob(job_id="j", source=SourceSpec(uri="file.mp4", duration_seconds=5))
    state = RachelLoopPipeline().dry_run(job)
    assert state.stage == Stage.ANALYZE
    assert state.error is None
