from rachel_loop_engine.manifest import dump_job, load_job
from rachel_loop_engine.models import QcResult, SourceSpec, VariantArtifact, VideoJob


def test_manifest_roundtrip(tmp_path):
    job = VideoJob(job_id="j1", source=SourceSpec(uri="https://x.test/v.mp4", duration_seconds=12))
    job.metadata["descript_project_id"] = "project-7"
    job.artifacts.append(
        VariantArtifact(
            kind="natural",
            project_id="project-7",
            composition_id="comp-a",
            share_url="https://example.test/a",
            qc=QcResult(passed=True, score=97.5, warnings=["minor"]),
        )
    )
    p = dump_job(job, tmp_path / "job.json")
    loaded = load_job(p)
    assert loaded.job_id == "j1"
    assert loaded.source_duration == 12
    assert loaded.metadata["descript_project_id"] == "project-7"
    assert loaded.artifacts[0].share_url == "https://example.test/a"
    assert loaded.artifacts[0].qc is not None
    assert loaded.artifacts[0].qc.score == 97.5
