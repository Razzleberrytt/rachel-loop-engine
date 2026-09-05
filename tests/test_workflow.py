from pathlib import Path
from rachel_loop_engine.adapters import DescriptAdapter, MockDescriptTransport
from rachel_loop_engine.models import SourceSpec, VideoJob
from rachel_loop_engine.prompts import PromptBook
from rachel_loop_engine.workflow import DescriptWorkflowRunner

def test_multivariant_workflow():
    t = MockDescriptTransport()
    runner = DescriptWorkflowRunner(DescriptAdapter(t), PromptBook(Path(__file__).parents[1]))
    job = VideoJob(job_id="abc", source=SourceSpec(uri="https://x.test/raw.mp4", duration_seconds=20))
    pid = runner.prepare_variants(job)
    assert pid == "project-1"
    result = runner.publish_variants(job)
    assert len(result.artifacts) == 3
    assert {a.kind for a in result.artifacts} == {"natural", "retention", "loop"}
