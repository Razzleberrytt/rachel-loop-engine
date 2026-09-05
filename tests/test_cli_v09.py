import json
from pathlib import Path

from rachel_loop_engine.cli import main
from rachel_loop_engine.manifest import dump_job
from rachel_loop_engine.models import SourceSpec, VideoJob


def test_plan_smart_cli_writes_real_text_and_no_text_controls(tmp_path: Path):
    job = VideoJob("j", SourceSpec("private://clip", 8), premise="baby reaction")
    manifest = dump_job(job, tmp_path / "job.json")
    out = tmp_path / "plans"
    code = main([
        "plan-smart", str(manifest), "--head-trim", "0.5", "--loop-anchor", "4",
        "--payoff", "6:7", "--text", "watch her eyes", "--out-dir", str(out),
    ])
    assert code == 0
    retention = json.loads((out / "retention.json").read_text())
    no_text = json.loads((out / "minimal_text.json").read_text())
    assert retention["text_overlays"][0]["text"] == "watch her eyes"
    assert no_text["text_overlays"] == []


def test_screenshot_metrics_cli_attaches_hash_and_variant_duration(tmp_path: Path):
    job = VideoJob("j", SourceSpec("private://clip", 10))
    job.metadata["creative_fingerprints"] = {
        "loop": {"fingerprint_id": "abc123", "duration_seconds": 5.0}
    }
    manifest = dump_job(job, tmp_path / "job.json")
    screenshot = tmp_path / "shot.png"
    screenshot.write_bytes(b"analytics-shot")
    output = tmp_path / "metrics.jsonl"
    code = main([
        "record-screenshot-metrics", str(manifest), str(screenshot),
        "--platform", "youtube_shorts", "--variant", "loop", "--views", "1000",
        "--apv", "200%", "--confidence", ".99", "--out", str(output),
    ])
    assert code == 0
    record = json.loads(output.read_text().strip())
    assert record["metrics"]["video_duration_seconds"] == 5.0
    assert record["creative_fingerprint_id"] == "abc123"
    assert record["provenance"]["source_kind"] == "analytics_screenshot"
    assert len(record["provenance"]["source_sha256"]) == 64
