from rachel_loop_engine.cli import main
from rachel_loop_engine.manifest import dump_job
from rachel_loop_engine.models import SourceSpec, VariantArtifact, VideoJob
from rachel_loop_engine.review import MediaReview, review_to_dict


def test_review_card_cli(tmp_path, capsys):
    job = VideoJob(job_id="j", source=SourceSpec(uri="https://x.test/v.mp4", duration_seconds=4))
    review = MediaReview("natural", True, 92, 5, 4.5, 4.3)
    job.artifacts.append(VariantArtifact(kind="natural", metadata={"media_review": review_to_dict(review)}))
    path = dump_job(job, tmp_path / "job.json")
    assert main(["review-card", str(path)]) == 0
    out = capsys.readouterr().out
    assert "**Recommended:** natural" in out
