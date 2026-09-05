import json

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


def test_record_metrics_cli_accepts_percent_and_appends_snapshot(tmp_path, capsys):
    job = VideoJob(job_id="j-loop", source=SourceSpec(uri="private", duration_seconds=5.8))
    path = dump_job(job, tmp_path / "job.json")
    out_path = tmp_path / "metrics.jsonl"
    assert main([
        "record-metrics",
        str(path),
        "--platform", "youtube_shorts",
        "--variant", "C Loop",
        "--views", "2500",
        "--apv", "215%",
        "--likes", "100",
        "--shares", "25",
        "--out", str(out_path),
    ]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["derived"]["average_watch_ratio"] == 2.15
    assert payload["derived"]["shares_per_1000_views"] == 10.0
    assert out_path.exists()
