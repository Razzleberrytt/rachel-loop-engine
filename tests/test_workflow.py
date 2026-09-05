from pathlib import Path

from rachel_loop_engine.adapters import DescriptAdapter, MockDescriptTransport
from rachel_loop_engine.models import SourceSpec, VideoJob
from rachel_loop_engine.prompts import PromptBook
from rachel_loop_engine.workflow import DescriptWorkflowRunner


def _runner(transport):
    return DescriptWorkflowRunner(DescriptAdapter(transport), PromptBook(Path(__file__).parents[1]))


def test_multivariant_workflow():
    t = MockDescriptTransport()
    runner = _runner(t)
    job = VideoJob(job_id="abc", source=SourceSpec(uri="https://x.test/raw.mp4", duration_seconds=20))
    pid = runner.prepare_variants(job)
    assert pid == "project-1"
    assert set(job.metadata["descript_compositions"]) == {"natural", "retention", "loop"}
    result = runner.publish_variants(job)
    assert len(result.artifacts) == 3
    assert {a.kind for a in result.artifacts} == {"natural", "retention", "loop"}


def test_prepare_is_idempotent_when_canonical_variants_exist():
    t = MockDescriptTransport()
    runner = _runner(t)
    job = VideoJob(job_id="abc", source=SourceSpec(uri="https://x.test/raw.mp4", duration_seconds=20))
    job.metadata["descript_project_id"] = "project-1"

    runner.prepare_variants(job)

    names = [name for name, _ in t.calls]
    assert "import_media" not in names
    assert "run_agent" not in names
    assert names.count("get_project") >= 1


def test_publish_reuses_existing_artifacts():
    t = MockDescriptTransport()
    runner = _runner(t)
    job = VideoJob(job_id="abc", source=SourceSpec(uri="https://x.test/raw.mp4", duration_seconds=20))
    runner.prepare_variants(job)
    first = runner.publish_variants(job, kinds=("natural",))
    second = runner.publish_variants(job, kinds=("natural",))
    assert first.artifacts[0].share_url == second.artifacts[0].share_url
    names = [name for name, _ in t.calls]
    assert names.count("publish") == 1
    assert second.reused_variants
