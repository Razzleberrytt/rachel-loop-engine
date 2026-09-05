from rachel_loop_engine.manifest import dump_job, load_job
from rachel_loop_engine.models import SourceSpec, VideoJob

def test_manifest_roundtrip(tmp_path):
    job = VideoJob(job_id="j1", source=SourceSpec(uri="https://x.test/v.mp4", duration_seconds=12))
    p = dump_job(job, tmp_path / "job.json")
    loaded = load_job(p)
    assert loaded.job_id == "j1"
    assert loaded.source_duration == 12
